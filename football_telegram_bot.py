import http.client
import json
from telegram.ext import Updater, CommandHandler
import telegram

# Italian Serie A is always the default league for all commands

leagues = {"BSA": 444, "PL": 445, "ELC": 446, "EL1": 447, "EL2": 448,
           "DED": 449, "FL1": 450, "FL2": 451, "BL1": 452, "BL2": 453,
           "PD": 455, "SA": 456, "PPL": 457, "SB": 459,
           "CL": 464}

leaguesId = {444: "BSA", 445: "PL", 446: "ELC", 447: "EL1", 448: "EL2",
             449: "DED", 450: "FL1", 451: "FL2", 452: "BL1", 453: "BL2",
             455: "PD", 456: "SA", 457: "PPL", 459: "SB",
             464: "CL"}
competitions_ids = {444: "Brazilian Serie A", 445: "Premier League", 446: "Championship", 447: "League One", 448: "League Two",
             449: "Eredivisie", 450: "Ligue 1", 451: "Ligue 2", 452: "Bundesliga", 453: "2. Bundesliga",
             455: "La Liga", 456: "Serie A", 457: "Primeira Liga", 459: "Serie B",
             464: "Champions League"}

teamsSA = {"Juventus": 109,"Cagliari Calcio": 104,"Hellas Verona FC": 450,"SSC Napoli": 113,"Atalanta BC": 102,"AS Roma": 100,"Udinese Calcio": 115,"AC Chievo Verona": 106,"US Sassuolo Calcio": 471,"Genoa CFC": 107,"UC Sampdoria": 584,"Benevento Calcio": 1106,"SS Lazio": 110,"SPAL Ferrara": 1107,"FC Internazionale": 108,"ACF Fiorentina": 99,"Bologna FC": 103,"Torino FC": 586,"FC Crotone": 472,"AC Milan": 98}
teamsPD = {"CD Leganes": 745,"Deportivo Alavés": 263,"Valencia CF": 95,"UD Las Palmas": 275,"RC Celta de Vigo": 558,"Real Sociedad de Fútbol": 92,"Girona FC": 298,"Club Atlético de Madrid": 78,"Sevilla FC": 559,"RCD Espanyol": 80,"Athletic Club": 77,"Getafe CF": 82,"FC Barcelona": 81,"Real Betis": 90,"RC Deportivo La Coruna": 560,"Real Madrid CF": 86,"Levante UD": 88,"Villarreal CF": 94,"Málaga CF": 84,"SD Eibar": 278}
teamsPL = {"Arsenal FC": 57,"Leicester City FC": 338,"Watford FC": 346,"Liverpool FC": 64,"Southampton FC": 340,"Swansea City FC": 72,"West Bromwich Albion FC": 74,"AFC Bournemouth": 1044,"Everton FC": 62,"Stoke City FC": 70,"Crystal Palace FC": 354,"Huddersfield Town": 394,"Chelsea FC": 61,"Burnley FC": 328,"Brighton & Hove Albion": 397,"Manchester City FC": 65,"Newcastle United FC": 67,"Tottenham Hotspur FC": 73,"Manchester United FC": 66,"West Ham United FC": 563}
teamsBL1 = {"FC Bayern München": 5,"Bayer Leverkusen": 3,"Hamburger SV": 7,"FC Augsburg": 16,"Hertha BSC": 9,"VfB Stuttgart": 10,"TSG 1899 Hoffenheim": 2,"Werder Bremen": 12,"1. FSV Mainz 05": 15,"Hannover 96": 8,"VfL Wolfsburg": 11,"Borussia Dortmund": 4,"FC Schalke 04": 6,"Red Bull Leipzig": 721,"SC Freiburg": 17,"Eintracht Frankfurt": 19,"Bor. Mönchengladbach": 18,"1. FC Köln": 1,"VfL Bochum": 36,"FC St. Pauli": 20,"FC Ingolstadt 04": 31,"1. FC Union Berlin": 28,"Arminia Bielefeld": 38,"Jahn Regensburg": 43,"SV Darmstadt 98": 55,"SpVgg Greuther Fürth": 21,"1. FC Nürnberg": 14,"1. FC Kaiserslautern": 13,"Dynamo Dresden": 35,"MSV Duisburg": 25,"Holstein Kiel": 720,"SV Sandhausen": 46,"1. FC Heidenheim 1846": 44,"Erzgebirge Aue": 22,"Fortuna Düsseldorf": 24,"Eintracht Braunschweig": 33}
teamsSB = {"Parma FC": 112,"Cremonese": 457,"Virtus Entella": 747,"Perugia": 452,"Venezia": 454,"Salernitana Calcio": 455,"Ternana Calcio": 479,"Empoli FC": 445,"Pro Vercelli": 590,"Frosinone Calcio": 470,"US Città di Palermo": 114,"Spezia Calcio": 488,"AS Cittadella": 466,"Ascoli": 446,"Carpi FC": 713,"Novara Calcio": 587,"AS Avellino 1912": 486,"Brescia Calcio": 449,"Pescara Calcio": 585,"Foggia": 1822,"AS Bari": 431,"AC Cesena": 591}
teamsSSA = {"EC Flamengo": 1783,"Atlético Mineiro": 1766,"Corinthians": 1779,"Chapecoense": 1772,"Fluminense FC": 1765,"Santos FC": 1774,"Bahia": 1777,"Atlético PR": 1768,"Ponte Preta": 1781,"Sport Recife": 1778,"Palmeiras": 1769,"Vasco da Gama": 1780,"Cruzeiro": 1771,"Sao Paulo": 1776,"Avaí SC": 1775,"EC Vitória": 1782,"Grémio": 1767,"Botafogo": 1770,"Coritiba FC": 1773,"Atlético Goianiense": 1764}
teamsEN = {"Sunderland AFC": 71 ,"Derby County": 342 ,"Nottingham Forest": 351 ,"Millwall FC": 384 ,"Bristol City": 387 ,"Barnsley FC": 357 ,"Wolverhampton Wanderers FC": 76 ,"Middlesbrough FC": 343 ,"Sheffield United FC": 356 ,"Brentford FC": 402 ,"Queens Park Rangers": 69 ,"Reading": 355 ,"Preston North End": 1081 ,"Sheffield Wednesday": 345 ,"Ipswich Town": 349 ,"Birmingham City": 332 ,"Fulham FC": 63 ,"Norwich City FC": 68 ,"Burton Albion FC": 1072 ,"Cardiff City FC": 715 ,"Aston Villa FC": 58 ,"Hull City FC": 322 ,"Bolton Wanderers FC": 60 ,"Leeds United": 341 ,"Bradford City AFC": 1067 ,"Blackpool FC": 336 ,"Shrewsbury Town FC": 1080 ,"Northampton Town": 376 ,"Scunthorpe United FC": 1078 ,"AFC Wimbledon": 347 ,"Portsmouth": 325 ,"Rochdale AFC": 361 ,"Peterborough United FC": 1077 ,"Plymouth Argyle": 1138 ,"Oldham Athletic AFC": 1075 ,"Oxford United": 1082 ,"Milton Keynes Dons": 409 ,"Wigan Athletic FC": 75 ,"Fleetwood Town FC": 1073 ,"Rotherham United": 385 ,"Doncaster Rovers FC": 1071 ,"Gillingham FC": 370 ,"Charlton Athletic": 348 ,"Bristol Rovers": 400 ,"Bury FC": 1068 ,"Walsall FC": 369 ,"Southend United FC": 1069 ,"Blackburn Rovers FC": 59 ,"Accrington Stanley": 1145 ,"Colchester United FC": 365 ,"Stevenage FC": 1144 ,"Newport County": 1142 ,"Morecambe FC": 1141 ,"Cheltenham Town": 411 ,"Luton Town": 389 ,"Yeovil Town": 1131 ,"Forest Green Rovers": 1130 ,"Barnet FC": 1134,"Exeter City": 1135,"Cambridge United": 1147,"Crewe Alexandra FC": 1074,"Mansfield Town": 1133,"Crawley Town": 1132,"Port Vale FC": 393,"Coventry City FC": 1076,"Notts County": 391,"Chesterfield FC": 363,"Grimsby Town": 1137,"Carlisle United": 1136,"Swindon Town FC": 1079,"Wycombe Wanderers": 1146,"Lincoln City": 1126}
teamsDED = {"ADO Den Haag": 680,"FC Utrecht": 676,"PSV Eindhoven": 674,"AZ Alkmaar": 682,"VVV Venlo": 668,"Sparta Rotterdam": 1085,"Heracles Almelo": 671,"Ajax Amsterdam": 678,"Vitesse Arnhem": 679,"NAC Breda": 681,"PEC Zwolle": 684,"Roda JC Kerkrade": 665,"Feyenoord Rotterdam": 675,"FC Twente Enschede": 666,"Willem II Tilburg": 672,"Excelsior": 670,"FC Groningen": 677,"SC Heerenveen": 673}
teamsFL1 = {"AS Monaco FC": 548,"Toulouse FC": 511,"Paris Saint-Germain": 524,"Amiens SC": 530,"ES Troyes AC": 531,"Stade Rennais FC": 529,"AS Saint-Étienne": 527,"OGC Nice": 522,"Olympique Lyonnais": 523,"RC Strasbourg Alsace": 576,"Montpellier Hérault SC": 518,"SM Caen": 514,"FC Metz": 545,"EA Guingamp": 538,"OSC Lille": 521,"FC Nantes": 543,"Angers SCO": 532,"FC Girondins de Bordeaux": 526,"Olympique de Marseille": 516,"Dijon FCO": 528}
teamsFL2 = {"US Orleans": 742,"AS Nancy": 520,"Paris FC": 1045,"Clermont Foot Auvergne": 541,"Stade Brestois": 512,"LB Châteauroux": 539,"Nîmes Olympique": 556,"Stade de Reims": 547,"Chamois Niortais FC": 557,"Ajaccio AC": 510,"FC Valenciennes": 515,"Gazélec Ajaccio": 555,"Sochaux FC": 517,"FC Bourg-en-Bresse Péronnas": 1042,"RC Tours": 544,"Le Havre AC": 533,"FC Lorient": 525,"Quevilly Rouen": 1807,"AJ Auxerre": 519,"RC Lens": 546}
teamsPPL = {"Desportivo Aves": 1809,"Sporting CP": 498,"Vitoria Setubal": 506,"Moreirense FC": 583,"Portimonense S.C.": 1808,"Boavista Porto FC": 810,"Feirense": 500,"CD Tondela": 1049,"FC Rio Ave": 496,"C.F. Os Belenenses": 711,"Maritimo Funchal": 504,"FC Paços de Ferreira": 507,"FC Porto": 503,"GD Estoril Praia": 582,"SL Benfica": 495,"Sporting Braga": 497,"Vitoria Guimaraes": 502,"G.D. Chaves": 591}
teamsCL = {"SL Benfica": 495,"CSKA Moscow": 751,"Olympiacos F.C.": 654,"Sporting CP": 498,"FC Barcelona": 81,"Juventus Turin": 109,"AS Roma": 100,"Club Atlético de Madrid": 78,"Chelsea FC": 61,"Qarabag Agdam FK": 611,"Celtic FC": 732,"Paris Saint-Germain": 524,"FC Bayern München": 5,"RSC Anderlecht": 726,"Manchester United FC": 66,"FC Basel": 729,"Real Madrid CF": 86,"APOEL Nicosia": 752,"Red Bull Leipzig": 721,"AS Monaco FC": 548,"FC Porto": 503,"Besiktas JK": 600,"Shakhtar Donetsk": 724,"SSC Napoli": 113,"Feyenoord Rotterdam": 675,"Manchester City FC": 65,"NK Maribor": 734,"Spartak Moskva": 754,"Liverpool FC": 64,"Sevilla FC": 559,"Tottenham Hotspur FC": 73,"Borussia Dortmund": 4}

BSA_ids = {1783: "EC Flamengo", 1766: "Atlético Mineiro", 1779: "Corinthians", 1772: "Chapecoense", 1765: "Fluminense", 1774: "Santos", 1777: "Bahia", 1768: "Atlético PR", 1781: "Ponte Preta", 1778: "Sport Recife",1769: "Palmeiras", 1780: "Vasco da Gama", 1771: "Cruzeiro", 1776: "Sao Paulo", 1775: "Avaí SC", 1782: "EC Vitória", 1767: "Grémio", 1770: "Botafogo", 1773: "Coritiba", 1764: "Atlético Goianiense"}
PL_ids = {57: "Arsenal", 338: "Leicester City", 346: "Watford", 64: "Liverpool", 340: "Southampton", 72: "Swansea City", 74: "West Bromwich Albion", 1044: "Bournemouth", 62: "Everton", 70: "Stoke City", 354: "Crystal Palace",394: "Huddersfield Town", 61: "Chelsea", 328: "Burnley", 397: "Brighton & Hove Albion", 65: "Manchester City", 67: "Newcastle United", 73: "Tottenham Hotspur", 66: "Manchester United", 563: "West Ham United"}
ELC_ids = {71: "Sunderland", 342: "Derby County", 351: "Nottingham Forest", 384: "Millwall", 387: "Bristol City", 357: "Barnsley", 76: "Wolverhampton Wanderers", 343: "Middlesbrough", 356: "Sheffield United", 402: "Brentford", 69: "Queens Park Rangers", 355: "Reading",1081: "Preston North End", 345: "Sheffield Wednesday", 349: "Ipswich Town", 332: "Birmingham City", 63: "Fulham", 68: "Norwich City", 1072: "Burton Albion", 715: "Cardiff City", 58: "Aston Villa", 322: "Hull City", 60: "Bolton Wanderers", 341: "Leeds United"}
EL1_ids = {1067: "Bradford City", 336: "Blackpool", 1080: "Shrewsbury Town", 376: "Northampton Town", 1078: "Scunthorpe United", 347: "Wimbledon", 325: "Portsmouth", 361: "Rochdale", 1077: "Peterborough United", 1138: "Plymouth Argyle", 1075: "Oldham Athletic", 1082: "Oxford United",409: "Milton Keynes Dons", 75: "Wigan Athletic", 1073: "Fleetwood Town", 385: "Rotherham United", 1071: "Doncaster Rovers", 370: "Gillingham", 348: "Charlton Athletic", 400: "Bristol Rovers", 1068: "Bury", 369: "Walsall", 1069: "Southend United", 59: "Blackburn Rovers"}
EL2_ids = {1145: "Accrington Stanley", 365: "Colchester United", 1144: "Stevenage", 1142: "Newport County", 1141: "Morecambe", 411: "Cheltenham Town", 389: "Luton Town", 1131: "Yeovil Town", 1130: "Forest Green Rovers", 1134: "Barnet", 1135: "Exeter City", 1147: "Cambridge United",1074: "Crewe Alexandra", 1133: "Mansfield Town", 1132: "Crawley Town", 393: "Port Vale", 1076: "Coventry City", 391: "Notts County", 363: "Chesterfield", 1137: "Grimsby Town", 1136: "Carlisle United", 1079: "Swindon Town", 1146: "Wycombe Wanderers", 1126: "Lincoln City"}
DED_ids = {680: "ADO Den Haag", 676: "FC Utrecht", 674: "PSV Eindhoven", 682: "AZ Alkmaar", 668: "VVV Venlo", 1085: "Sparta Rotterdam", 671: "Heracles Almelo", 678: "Ajax Amsterdam", 679: "Vitesse Arnhem",681: "NAC Breda", 684: "PEC Zwolle", 665: "Roda JC Kerkrade", 675: "Feyenoord Rotterdam", 666: "FC Twente Enschede", 672: "Willem II Tilburg", 670: "Excelsior", 677: "FC Groningen", 673: "SC Heerenveen"}
FL1_ids = {548: "Monaco", 511: "Toulouse", 524: "Paris Saint-Germain", 530: "Amiens SC", 531: "ES Troyes AC", 529: "Stade Rennais", 527: "Saint-Étienne", 522: "OGC Nice", 523: "Olympique Lyonnais", 576: "Strasbourg Alsace",518: "Montpellier Hérault", 514: "SM Caen", 545: "FC Metz", 538: "EA Guingamp", 521: "OSC Lille", 543: "FC Nantes", 532: "Angers SCO", 526: "Girondins de Bordeaux", 516: "Olympique de Marseille", 528: "Dijon"}
FL2_ids = {742: "US Orleans", 520: "Nancy", 1045: "Paris", 541: "Clermont Foot Auvergne", 512: "Stade Brestois", 539: "LB Châteauroux", 556: "Nîmes Olympique", 547: "Stade de Reims", 557: "Chamois Niortais", 510: "Ajaccio AC",515: "FC Valenciennes", 555: "Gazélec Ajaccio", 517: "Sochaux", 1042: "Bourg-en-Bresse Péronnas", 544: "RC Tours", 533: "Le Havre AC", 525: "FC Lorient", 1807: "Quevilly Rouen", 519: "AJ Auxerre", 546: "RC Lens"}
BL1_ids = { 5: "Bayern München", 3: "Bayer Leverkusen", 7: "Hamburger SV",16: "Augsburg",9: "Hertha BSC",10: "VfB Stuttgart",2: "TSG 1899 Hoffenheim",12: "Werder Bremen",15: "1. FSV Mainz 05",8: "Hannover 96",11: "VfL Wolfsburg",4: "Borussia Dortmund",6: "Schalke 04",721: "Red Bull Leipzig",17: "SC Freiburg",19: "Eintracht Frankfurt",18: "Bor. Mönchengladbach",1: "1. Köln"}
BL2_ids = {36: "VfL Bochum",20: "St. Pauli",31: "Ingolstadt 04",28: "1. Union Berlin",38: "Arminia Bielefeld",43: "Jahn Regensburg",55: "SV Darmstadt 98",21: "SpVgg Greuther Fürth",14: "1. Nürnberg",13: "1. Kaiserslautern",35: "Dynamo Dresden",25: "MSV Duisburg",720: "Holstein Kiel",46: "SV Sandhausen",44: "1. Heidenheim 1846",22: "Erzgebirge Aue",24: "Fortuna Düsseldorf",33: "Eintracht Braunschweig"}
PD_ids = {745: "CD Leganes",263: "Deportivo Alavés",95: "Valencia CF",275: "UD Las Palmas",558: "RC Celta de Vigo",92: "Real Sociedad",298: "Girona",78: "Atlético de Madrid",559: "Sevilla",80: "RCD Espanyol",77: "Athletic Club",82: "Getafe CF",81: "FC Barcelona",90: "Real Betis",560: "Deportivo La Coruña",86: "Real Madrid CF",88: "Levante UD",94: "Villarreal CF",84: "Málaga CF",278: "SD Eibar"}
SA_ids = {109: "Juventus",104: "Cagliari",450: "Hellas Verona",113: "Napoli",102: "Atalanta",100: "Roma",115: "Udinese",106: "Chievo Verona",471: "Sassuolo",107: "Genoa",584: "Sampdoria",1106: "Benevento",110: "Lazio",1107: "SPAL Ferrara",108: "Inter",99: "Fiorentina",103: "Bologna",586: "Torino",472: "Crotone",98: "Milan"}
PPL_ids = {1809: "Desportivo Aves",498: "Sporting CP",506: "Vitoria Setubal",583: "Moreirense",1808: "Portimonense S.C.",810: "Boavista Porto",500: "Feirense",1049: "CD Tondela",496: "FC Rio Ave",711: "C.F. Os Belenenses",504: "Maritimo Funchal",507: "FC Paços de Ferreira",503: "FC Porto",582: "GD Estoril Praia",495: "SL Benfica",497: "Sporting Braga",502: "Vitoria Guimaraes",1103: "G.D. Chaves"}
SB_ids = {112: "Parma",457: "Cremonese",747: "Virtus Entella",452: "Perugia",454: "Venezia",455: "Salernitana",479: "Ternana",445: "Empoli",590: "Pro Vercelli",470: "Frosinone",114: "Palermo",488: "Spezia",466: "Cittadella",446: "Ascoli",713: "Carpi",587: "Novara",486: "Avellino",449: "Brescia",585: "Pescara",1822: "Foggia",431: "Bari",591: "Cesena"}
CL_ids = {495 :"Benfica",751 :"CSKA Moscow",654 :"Olympiacos",498 :"Sporting CP",81 :"Barcelona",109 :"Juventus",100 :"Roma",78 :"Atlético de Madrid",61 :"Chelsea",611 :"Qarabag Agdam FK",732 :"Celtic",524 :"Paris Saint-Germain",5 :"Bayern München",726 :"Anderlecht",66 :"Manchester United",729 :"Basel",86 :"Real Madrid",752 :"APOEL Nicosia",721 :"Red Bull Leipzig",548 :"AS Monaco",503 :"Porto",600 :"Besiktas JK",724 :"Shakhtar Donetsk",113 :"Napoli",675 :"Feyenoord",65 :"Manchester City",734 :"NK Maribor",754 :"Spartak Moskva",64 :"Liverpool",559 :"Sevilla",73 :"Tottenham Hotspur",4 :"Borussia Dortmund"}

leagues_teams_ids = {444: BSA_ids, 445: PL_ids, 446: ELC_ids, 447: EL1_ids, 448: EL2_ids,
             449: DED_ids, 450: FL1_ids, 451: FL2_ids, 452: BL1_ids, 453: BL2_ids,
             455: PD_ids, 456: SA_ids, 457: PPL_ids, 459: SB_ids,
             464: CL_ids}

# insert your own API token from http://football-data.org
api_token = ""
headers = {"X-Auth-Token": api_token,
               "X-Response-Control": "minified"}


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
      return None
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
    string = "*{0:s}*\nMatchday {1:2d}\n{2:s}".format(
        response["leagueCaption"], response["matchday"], "\n".join(ranks))
    return string


# posts table of league
def table(bot, update, args):
    print("Getting table...")
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
    print("Done!")
    return


def parse_fixtures(response, league_id, matchday, flag):
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
            date = fixture["date"]
            date = date[0:10] + " " + str(int(date[11:13]) + 1) + date[13:len(date)-4]
            fixtures.append("{0:s}\n``` {1:>13s} {2:d} - {3:d} {4:s}```\n".format(date, leagues_teams_ids[league_id][fixture["homeTeamId"]], home_goals, away_goals, leagues_teams_ids[league_id][fixture["awayTeamId"]]))
    string = "*{0:s}*\nMatchday {1:d}\n\n{2:s}".format(competitions_ids[league_id], matchday, "\n".join(fixtures))
    return string


def get_league_matchday(connection, args, flag):
    # get league id
    try:
        league_id = leagues[args[0].upper()]
    except Exception as e:
        league_id = 456
    # if live/remaining get getCurrentMatchday
    if flag != 0:
        table = get_table(connection, league_id)
        matchday = table["matchday"]
    # else try to read matchday from args
    elif flag == 0:
        if len(args) == 1:
            try:
                matchday = int(args[0])
            except Exception as e:
                table = get_table(connection, league_id)
                matchday = table["matchday"]
        else:
            try:
                matchday = int(args[1])
            except Exception as e:
                table = get_table(connection, league_id)
                matchday = table["matchday"]
    return league_id, matchday


# get fixtures for league and matchday
# flag == 0 for whole matchday
# flag == 1 for live games in matchday
# flag == 2 for remaining games in matchday, includes live games
def get_fixtures(bot, args, flag, update):
    connection = get_connection(bot)
    if connection is None:
        return
    league_id, matchday = get_league_matchday(connection, args, flag)
    try:
        connection.request("GET", "/v1/competitions/{}/fixtures?matchday={}".format(league_id, matchday), None, headers)
    except Exception as e:
        error(bot)
        return
    response = json.loads(connection.getresponse().read().decode())
    string = parse_fixtures(response, league_id, matchday, flag)
    bot.send_message(chat_id=update.message.chat_id,
                     text=string, parse_mode="markdown")
    print("Done!")
    return


# gets fixtures for matchday and league
def fixtures(bot, update, args):
    print("Getting fixtures...")
    flag = 0
    get_fixtures(bot, args, flag, update)
    return


# gets live fixtures for league
def live(bot, update, args):
    print("Getting live fixtures...")
    flag = 1
    get_fixtures(bot, args, flag, update)
    return


# gets remaining fixtures for league
def remaining(bot, update, args):
    print("Getting remaining fixtures...")
    flag = 2
    get_fixtures(bot, args, flag, update)
    return


# start/help message
def start(bot, update):
    string = "`/help ` command list\n`/table [league-code]` shows table for selected league\n`/fixtures [league-code] [matchday] ` shows fixtures for selected league and matchday\n`/live [league-code] ` shows live fixtures for selected league\n`/remaining [league-code] ` shows remaining fixtures for selected league\n`/team [team-name] [days]` shows fixture for team in the following days (all competitions)\n\nLeague codes:\n`BSA`  Brazilian Serie A\n`PL `  Premier League\n`ELC`  Championship\n`EL1`  League One\n`EL2`  League Two\n`DED`  Eredivisie\n`FL1`  Ligue 1\n`FL2`  Ligue 2\n`BL1`  Bundesliga\n`BL2`  2. Bundesliga\n`PD `  La Liga\n`SA `  Serie A\n`PPL`  Primeira Liga\n`DFB`  DFB Pokal\n`SB `  Serie B\n`CL `  Champions League"
    bot.send_message(chat_id=update.message.chat_id,
                     text=string, parse_mode="markdown")
    return


# get fixtures for team for following days
def get_team(bot, update, args):
    team = args[0].lower()
    print("Getting team fixtures for", team)
    connection = get_connection(bot)
    if connection is None:
        return
    # gets days from args
    try:
        days = int(args[1])
    except Exception as e:
        days = 15
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
    connection.request("GET", "/v1/teams/{}/fixtures?timeFrame=n{}".format(team_id, days), None, headers)
    response = json.loads(connection.getresponse().read().decode())
    fixtures = []
    for fixture in response["fixtures"]:
        date = fixture["date"]
        date = date[0:10] + " " + str(int(date[11:13]) + 1) + date[13:len(date)-4]
        fixtures.append("*{}* {} - _Matchday {}_\n{} - {}\n".format(competitions_ids[fixture["competitionId"]], date, fixture["matchday"], leagues_teams_ids[fixture["competitionId"]][fixture["homeTeamId"]], leagues_teams_ids[fixture["competitionId"]][fixture["awayTeamId"]]))
    string = "{}".format("\n".join(fixtures))
    bot.send_message(chat_id=update.message.chat_id,
                     text=string, parse_mode="markdown")
    print("Done!")
    return

# insert your own bot token
bot_token = ""
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
