import json
import copy
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chess_engine import ChessBoard, ChessAI, WHITE, BLACK

# In-memory game storage (use DB/cache in production)
games = {}

def get_or_create_game(game_id):
    if game_id not in games:
        games[game_id] = {'board': ChessBoard(), 'ai': ChessAI(depth=3)}
    return games[game_id]


def index(request):
    return render(request, 'chess_app/index.html')


@csrf_exempt
def new_game(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        game_id = data.get('game_id', 'default')
        difficulty = data.get('difficulty', 3)
        player_color = data.get('player_color', 'white')

        board = ChessBoard()
        ai = ChessAI(depth=int(difficulty))
        games[game_id] = {
            'board': board,
            'ai': ai,
            'player_color': WHITE if player_color == 'white' else BLACK
        }

        board_data = board.to_dict()
        board_data['player_color'] = player_color

        # If player is black, AI plays first
        if player_color == 'black':
            ai_move = ai.get_best_move(board)
            if ai_move:
                board.apply_move(ai_move)
                board_data = board.to_dict()
                board_data['player_color'] = player_color
                board_data['ai_move'] = ai_move

        return JsonResponse({'success': True, 'board': board_data})
    return JsonResponse({'error': 'POST required'}, status=400)


@csrf_exempt
def make_move(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        game_id = data.get('game_id', 'default')
        from_pos = tuple(data.get('from'))
        to_pos = tuple(data.get('to'))
        promotion = data.get('promotion')

        if game_id not in games:
            return JsonResponse({'error': 'Game not found'}, status=404)

        game = games[game_id]
        board = game['board']
        ai = game['ai']
        player_color = game.get('player_color', WHITE)

        # Get legal moves and find matching move
        legal_moves = board.get_legal_moves(board.current_turn)
        chosen_move = None
        for move in legal_moves:
            if move['from'] == from_pos and move['to'] == to_pos:
                if promotion:
                    if move.get('promotion') == promotion:
                        chosen_move = move
                        break
                else:
                    if 'promotion' not in move:
                        chosen_move = move
                        break

        if not chosen_move:
            # Check if promotion needed (return promotion choices)
            needs_promo = any(
                m['from'] == from_pos and m['to'] == to_pos and 'promotion' in m
                for m in legal_moves
            )
            if needs_promo:
                return JsonResponse({'needs_promotion': True, 'from': list(from_pos), 'to': list(to_pos)})
            return JsonResponse({'error': 'Illegal move'}, status=400)

        board.apply_move(chosen_move)
        board_data = board.to_dict()
        board_data['player_move'] = {'from': list(from_pos), 'to': list(to_pos)}

        if board.game_over:
            return JsonResponse({'success': True, 'board': board_data})

        # AI response
        if board.current_turn != player_color:
            ai_move = ai.get_best_move(board)
            if ai_move:
                board.apply_move(ai_move)
                board_data = board.to_dict()
                board_data['ai_move'] = {
                    'from': list(ai_move['from']),
                    'to': list(ai_move['to'])
                }
                if 'promotion' in ai_move:
                    board_data['ai_move']['promotion'] = ai_move['promotion']

        return JsonResponse({'success': True, 'board': board_data})
    return JsonResponse({'error': 'POST required'}, status=400)


@csrf_exempt
def get_legal_moves_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        game_id = data.get('game_id', 'default')
        row = data.get('row')
        col = data.get('col')

        if game_id not in games:
            return JsonResponse({'error': 'Game not found'}, status=404)

        board = games[game_id]['board']
        player_color = games[game_id].get('player_color', WHITE)

        piece = board.get_piece(row, col)
        if not piece or piece[1] != board.current_turn or piece[1] != player_color:
            return JsonResponse({'moves': []})

        all_legal = board.get_legal_moves(board.current_turn)
        piece_moves = [m for m in all_legal if m['from'] == (row, col)]
        moves_data = [{'to': list(m['to'])} for m in piece_moves]

        return JsonResponse({'moves': moves_data})
    return JsonResponse({'error': 'POST required'}, status=400)
