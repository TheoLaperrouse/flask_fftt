import uuid
import datetime
import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from src.connexion_api import connexion_api

app = FastAPI()

@app.get("/", response_class=RedirectResponse, status_code=302)
async def redirect_to_docs():
    '''Redirect to docs on /'''
    return "http://fastapifftt.thorigne-tt.net/docs"

@app.get("/players/{licence}")
def get_player_by_licence(licence: str):
    '''Get player by licence'''
    return connexion_api("xml_joueur", f"licence={licence}").get('joueur')


@app.get("/players/name/{last_name}_{first_name}")
def get_player_by_name(last_name: str, first_name: str):
    '''Get player by name'''
    return connexion_api("xml_liste_joueur_o", f"nom={last_name}&prenom={first_name}").get('joueur')


@app.get("/players/club/{num_club}")
def get_players_by_club(num_club: str):
    '''Get players by club num'''
    return connexion_api("xml_liste_joueur_o", f"club={num_club}").get('joueur')


@app.get("/matches/{licence}")
def get_match_by_licence(licence: str):
    '''Get last matches by licence'''
    return connexion_api("xml_partie", f"numlic={licence}").get('partie')


@app.get("/matches/club/{num_club}")
def get_matches_by_phase(num_club: str):
    '''Get all the matches of a club for a phase'''
    teams = get_teams_by_club(num_club)
    all_matches_by_team = [get_matches_poules_by_link(
        team["link"]) for team in teams]
    all_matches = [
        match for matches in all_matches_by_team for match in matches]
    return all_matches.sort(key=lambda match: datetime.datetime.strptime(match["date"], "%d/%m/%Y"))


@app.get("/teams/{num_club}")
def get_teams_by_club(num_club: str):
    '''Get team by club num'''
    return connexion_api("xml_equipe", f"numclu={num_club}").get("equipe")


@app.get("/proA")
def get_pro_a_stats():
    '''Get pro A statistics'''
    players = {}
    matches = get_matches_poules_by_link(get_pro_a())
    for match in [get_match_by_link(m['lien']) for m in matches]:
        if match:
            for individual_match in match:
                if individual_match and individual_match['ja'] and individual_match['jb']:
                    player_a, player_b = individual_match['ja'], individual_match['jb']
                    score_a = individual_match.get('scorea', -1) == '1'
                    players[player_a] = players.get(
                        player_a, {'vict': 0, 'matches': 0})
                    players[player_b] = players.get(
                        player_b, {'vict': 0, 'matches': 0})
                    players[player_a]['vict'] += score_a
                    players[player_b]['vict'] += not score_a
                    players[player_a]['matches'] += 1
                    players[player_b]['matches'] += 1
    for stats in players.values():
        stats['win_ratio'] = f'{stats["vict"] / stats["matches"]:.2f}'
    return sorted(players.items(), key=lambda x: x[1]['win_ratio'], reverse=True)


ALPHABET = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'


@app.get("/short_uuid_to_uuid/{short_uuid}")
def short_uuid_to_uuid(short_uuid):
    '''Convert short UUID to an UUID'''
    base = len(ALPHABET)
    uuid_int = sum(ALPHABET.index(c) * base ** i for i,
                   c in enumerate(reversed(short_uuid)))
    return str(uuid.UUID(int=uuid_int, version=4))


@app.get("/uuid_to_short_uuid/{uuidv4}")
def uuid_to_short_uuid(uuidv4):
    '''Convert an UUID to short UUID'''
    uuid_int = int(uuidv4.replace('-', ''), 16)
    base = len(ALPHABET)
    digits = []
    while uuid_int:
        uuid_int, remainder = divmod(uuid_int, base)
        digits.append(ALPHABET[remainder])
    return ''.join(reversed(digits))


def get_matches_poules_by_link(lien_div: str):
    '''Get matches poules with a link'''
    return connexion_api("xml_result_equ", lien_div).get('tour', [])


def get_match_by_link(lien_match: str):
    '''Get individuals matches with a link'''
    return connexion_api("xml_chp_renc", lien_match).get('partie', [])


def get_pro_a():
    '''Get the proA team'''
    for team in get_teams_by_club('03350060'):
        if 'FED_PRO A' in team['libdivision']:
            return team['liendivision']
    return None


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
