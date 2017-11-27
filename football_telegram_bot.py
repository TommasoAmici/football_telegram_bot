import http.client
import json
from telegram.ext import Updater, CommandHandler
import telegram
import datetime
import dateutil.parser
from football_tg_bot_const import *

# Italian Serie A is always the default league for all commands

headers = {"X-Auth-Token": api_token, "X-Response-Control": "minified"}


# parse date TZ -> UTC, add UTC offset, print string
def parse_date(date, time_zone, status):
    if status != "FINISHED":
        return (dateutil.parser.parse(date) + datetime.timedelta(hours=time_zone)).strftime("%a, %b %d %Y %H:%M")
    else:
        return (dateutil.parser.parse(date)).strftime("%a, %b %d %Y")


def parse_date_no_day(date, time_zone):
    return (dateutil.parser.parse(date) + datetime.timedelta(hours=time_zone)).strftime("%b %d %Y")


# posts error message to chat
def error(bot):
    bot.send_message(chat_id=update.message.chat_id,
                     text="``` There was something wrong, try again later... ```", parse_mode="markdown")
    return


# tries connection to API
def get_connection(bot):
    try:
        connection = http.client.HTTPConnection("api.football-data.org")
    except Exception as e:
        error(bot)
        connection = None
    return connection


# gets table from API
def get_table(connection, league_id):
    try:
        connection.request("GET", "/v1/competitions/{}/leagueTable".format(league_id), None, headers)
    except:
        error(bot)
        return
    return json.loads(connection.getresponse().read().decode())


# Champions League table is divided in groups, needs its own parsing
def CL_table(response):
    league_id = 464
    ranks = []
    for group in response["standings"]:
        ranks.append("\n*Group {}*".format(group))
        for rank in response["standings"][group]:
            ranks.append("``` {0:22s} {1:d} ```".format(leagues_teams_ids[league_id][rank["teamId"]], rank["points"]))
    return "*{0:s}*\nMatchday {1:2d}\n{2:s}".format(
        response["leagueCaption"], response["matchday"], "\n".join(ranks))


# posts table of league
def table(bot, update, args):
    connection = get_connection(bot)
    if connection is None:
        return
    try:
        league_id = leagues[args[0].upper()]
    except Exception as e:
        league_id = 456
    response = get_table(connection, league_id)
    if league_id == 464:
        string = CL_table(response)
    else:
        ranks = []
        for rank in response["standing"]:
            ranks.append("{0:2d} {1:22s} {2:d}".format(
                rank["rank"], leagues_teams_ids[league_id][rank["teamId"]], rank["points"]))
        string = "*{0:s}*\nMatchday {1:2d}\n```{2:s}```".format(
                  response["leagueCaption"], response["matchday"], "\n".join(ranks))
    bot.send_message(chat_id=update.message.chat_id,
                     text=string, parse_mode="markdown")
    return


# parse fixtures, generates formatted message
def parse_fixtures(response, league_id, matchday, flag, time_zone):
    fixtures = []
    for fixture in response["fixtures"]:
        if flag == 1 and fixture["status"] != "IN_PLAY":
            continue
        if flag == 2 and fixture["status"] == "FINISHED":
            continue
        else:
            home_goals = fixture["result"]["goalsHomeTeam"]
            away_goals = fixture["result"]["goalsAwayTeam"]
            if home_goals is None:
                home_goals = 0
            if away_goals is None:
                away_goals = 0
            fixtures.append("{0:s}\n``` {1:>13s} {2:d} - {3:d} {4:s}```\n".format(parse_date(fixture["date"], time_zone, fixture["status"]), leagues_teams_ids[league_id][fixture["homeTeamId"]], home_goals, away_goals, leagues_teams_ids[league_id][fixture["awayTeamId"]]))
    return "*{0:s}*\nMatchday {1:d}\n\n{2:s}".format(competitions_ids[league_id], matchday, "\n".join(fixtures))


# get current matchday for league_id
def get_matchday(connection, league_id):
    return get_table(connection, league_id)["matchday"]


# get time zone from arg
def get_tz(arg):
    try:
        time_zone = int(arg)
    except Exception as e:
        return 0
    return time_zone


# parse args from /fixtures/live/remaining command
def get_league_matchday(connection, args, flag):
    # get league id
    if not args:
            league_id = 456
            matchday = get_matchday(connection, league_id)
            time_zone = 0
    else:
        try:
            league_id = leagues[args[0].upper()]
        except Exception as e:
            league_id = 456
            # format args for later parsing
            args.insert(0, 0)
        # if live/remaining get current matchday and time zone
        if flag != 0:
            matchday = get_matchday(connection, league_id)
            for arg in args:
                time_zone = get_tz(arg)
        # else try to read matchday from args
        elif flag == 0:
            if len(args) == 2:
                try:
                    matchday = int(args[1])
                except Exception as e:
                    matchday = get_matchday(connection, league_id)
            else:   
                try:
                    matchday = int(args[1])
                except Exception as e:
                    matchday = get_matchday(connection, league_id)
                time_zone = get_tz(args[2])
    return league_id, matchday, time_zone


# get fixtures for league and matchday
# flag == 0 for whole matchday
# flag == 1 for live games in matchday
# flag == 2 for remaining games in matchday, includes live games
def get_fixtures(bot, args, flag, update):
    connection = get_connection(bot)
    if connection is None:
        return
    league_id, matchday, time_zone = get_league_matchday(connection, args, flag)
    try:
        connection.request("GET", "/v1/competitions/{}/fixtures?matchday={}".format(league_id, matchday), None, headers)
    except Exception as e:
        error(bot)
        return
    bot.send_message(chat_id=update.message.chat_id,
                     text=parse_fixtures(json.loads(connection.getresponse().read().decode()), league_id, matchday, flag, time_zone), parse_mode="markdown")
    return


# gets fixtures for matchday and league
def fixtures(bot, update, args):
    get_fixtures(bot, args, 0, update)
    return


# gets live fixtures for league
def live(bot, update, args):
    get_fixtures(bot, args, 1, update)
    return


# gets remaining fixtures for league
def remaining(bot, update, args):
    get_fixtures(bot, args, 2, update)
    return


# start/help message
def start(bot, update):
    string = "`/help ` command list\n`/table [league-code]` shows table for selected league\n`/fixtures [league-code] [matchday] [UTC-offset]` shows fixtures for selected league and matchday, e.g. `/fixtures SA 13 2`\n`/live [league-code] [UTC-offset]` shows live fixtures for selected league\n`/remaining [league-code] [UTC-offset]` shows remaining fixtures for selected league\n`/team [team-name] [days] [UTC-offset]` shows fixture for team in the following days (all competitions)\n\nLeague codes:\n`BSA`  Brazilian Serie A\n`PL `  Premier League\n`ELC`  Championship\n`EL1`  League One\n`EL2`  League Two\n`DED`  Eredivisie\n`FL1`  Ligue 1\n`FL2`  Ligue 2\n`BL1`  Bundesliga\n`BL2`  2. Bundesliga\n`PD `  La Liga\n`SA `  Serie A\n`PPL`  Primeira Liga\n`DFB`  DFB Pokal\n`SB `  Serie B\n`CL `  Champions League"
    bot.send_message(chat_id=update.message.chat_id,
                     text=string, parse_mode="markdown")
    return


# get fixtures for team for following days
def get_team(bot, update, args):
    team = args[0].lower()
    connection = get_connection(bot)
    if connection is None:
        return
    # gets days from args
    try:
        days = int(args[1])
    except Exception as e:
        days = 15
    try:
        time_zone = int(args[2])
    except Exception as e:
        time_zone = 0
    # looks through all teams of (almost) all leagues
    # order of popularity/frequency of query (just a guess)
    # TODO (?) add remaining leagues FL2, BL2, BSA, ELC, EL1, EL2
    team_id = 0
    if team_id == 0:
        for t in teamsSA:
            if team in t.lower():
                team_id = teamsSA[t]
                break
    if team_id == 0:
        for t in teamsPL:
            if team in t.lower():
                team_id = teamsPL[t]
                break
    if team_id == 0:
        for t in teamsSB:
            if team in t.lower():
                team_id = teamsSB[t]
                break
    if team_id == 0:
        for t in teamsCL:
            if team in t.lower():
                team_id = teamsCL[t]
                break
    if team_id == 0:
        for t in teamsPD:
            if team in t.lower():
                team_id = teamsPD[t]
                break
    if team_id == 0:
        for t in teamsBL1:
            if team in t.lower():
                team_id = teamsBL1[t]
                break
    if team_id == 0:
        for t in teamsFL1:
            if team in t.lower():
                team_id = teamsFL1[t]
                break
    if team_id == 0:
        for t in teamsDED:
            if team in t.lower():
                team_id = teamsDED[t]
                break
    if team_id == 0:
        for t in teamsPPL:
            if team in t.lower():
                team_id = teamsPPL[t]
                break
    if team_id == 0:
        return
    fixtures = []
    if days > 0:
        connection.request("GET", "/v1/teams/{}/fixtures?timeFrame=n{}".format(team_id, days), None, headers)
        response = json.loads(connection.getresponse().read().decode())
        for fixture in response["fixtures"]:
            fixtures.append("*{}* {}\n_Matchday {}_\n{} - {}\n".format(competitions_ids[fixture["competitionId"]], parse_date(fixture["date"], time_zone, fixture["status"]), fixture["matchday"], leagues_teams_ids[fixture["competitionId"]][fixture["homeTeamId"]], leagues_teams_ids[fixture["competitionId"]][fixture["awayTeamId"]]))
    elif days < 0:
        connection.request("GET", "/v1/teams/{}/fixtures?timeFrame=p{}".format(team_id, -days), None, headers)
        response = json.loads(connection.getresponse().read().decode())
        for fixture in response["fixtures"]:
            fixtures.append("*{}* {} - _Matchday {}_\n`{:>15s} {}-{} {}`\n".format(competitions_ids[fixture["competitionId"]], parse_date_no_day(fixture["date"], time_zone, fixture["status"]), fixture["matchday"], leagues_teams_ids[fixture["competitionId"]][fixture["homeTeamId"]], fixture["result"]["goalsHomeTeam"], fixture["result"]["goalsAwayTeam"], leagues_teams_ids[fixture["competitionId"]][fixture["awayTeamId"]]))
    bot.send_message(chat_id=update.message.chat_id,
                     text="{}".format("\n".join(fixtures)), parse_mode="markdown")
    return


bot = telegram.Bot(token=bot_token)
updater = Updater(bot_token)

# defines telegram commands
updater.dispatcher.add_handler(CommandHandler(["start", "help", "aiuto"], start))
updater.dispatcher.add_handler(CommandHandler('table', table, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('team', get_team, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('fixtures', fixtures, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('live', live, pass_args=True))
updater.dispatcher.add_handler(CommandHandler('remaining', remaining, pass_args=True))

# starts bot, waits for commands
updater.start_polling()
updater.idle()
