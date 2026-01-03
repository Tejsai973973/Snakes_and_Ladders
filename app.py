import streamlit as st
import random
import time
import pandas as pd

# 🎨 Colors
def color_cell(text, color):
    if color == "red":
        return f'<span style="color:red">{text}</span>'
    elif color == "green":
        return f'<span style="color:green">{text}</span>'
    elif color == "blue":
        return f'<span style="color:blue">{text}</span>'
    elif color == "yellow":
        return f'<span style="color:orange">{text}</span>'
    return text

# 🐍🪜 Snakes and ladders
snakes = {16: 6, 47: 26, 49: 11, 56: 53, 62: 19, 64: 60, 87: 24, 93: 73, 95: 75, 98: 78}
ladders = {2: 38, 4: 14, 9: 31, 21: 42, 28: 84, 36: 44, 51: 67, 71: 91, 80: 89}

# 🧠 Session state
if "positions" not in st.session_state:
    st.session_state.positions = {"P1": 0, "P2": 0}
if "current_player" not in st.session_state:
    st.session_state.current_player = "P1"
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "turn_completed" not in st.session_state:
    st.session_state.turn_completed = False
if "move_messages" not in st.session_state:
    st.session_state.move_messages = []

def roll_dice():
    return random.randint(1, 6)

# 🧱 Build board
def build_board():
    board_data = []
    for row in range(10, 0, -1):
        row_data = []
        start = (row - 1) * 10 + 1
        end = row * 10
        rng = range(start, end + 1) if row % 2 == 0 else range(end, start - 1, -1)

        for square in rng:
            cell = str(square).rjust(3)
            if square in snakes:
                cell = color_cell(f"S↓ {snakes[square]}", "red")
            elif square in ladders:
                cell = color_cell(f"L↑ {ladders[square]}", "green")

            for player, pos in st.session_state.positions.items():
                if pos == square:
                    cell = color_cell(player, "blue")

            row_data.append(cell)
        board_data.append(row_data)

    return pd.DataFrame(board_data)

def display_board():
    df = build_board()
    st.markdown(df.style.to_html(), unsafe_allow_html=True)
    st.markdown("---")

# 🏁 Start Zone
def display_start_zone():
    st.markdown("### 🏁 Start Zone")
    col1, col2 = st.columns(2)

    with col1:
        if st.session_state.positions["P1"] == 0:
            st.markdown(
                "<div style='padding:10px;border:2px dashed #1f77b4;border-radius:10px;text-align:center;'>"
                "<b>P1</b> waiting to start 🎯</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='padding:10px;border:2px solid #ccc;border-radius:10px;"
                "text-align:center;color:#999;'>P1 entered the board</div>",
                unsafe_allow_html=True
            )

    with col2:
        if st.session_state.positions["P2"] == 0:
            st.markdown(
                "<div style='padding:10px;border:2px dashed #1f77b4;border-radius:10px;text-align:center;'>"
                "<b>P2</b> waiting to start 🎯</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='padding:10px;border:2px solid #ccc;border-radius:10px;"
                "text-align:center;color:#999;'>P2 entered the board</div>",
                unsafe_allow_html=True
            )

    st.markdown("---")

# 🎢 Snake / ladder animation
def handle_snake_ladder(player, start, end):
    if start == end:
        return
    with st.spinner(f"{player} moving..."):
        step = 1 if end > start else -1
        steps = abs(end - start) + 1
        bar = st.progress(0)
        for i, pos in enumerate(range(start, end + step, step)):
            st.session_state.positions[player] = pos
            bar.progress(min((i + 1) / steps, 1.0))
            time.sleep(0.05)
        bar.empty()

# 🏁 App
st.title("🐍🪜 Snakes and Ladders - Human vs Computer")

if st.session_state.game_over:
    st.balloons()
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Play Again?"):
            st.session_state.positions = {"P1": 0, "P2": 0}
            st.session_state.current_player = "P1"
            st.session_state.game_over = False
            st.session_state.turn_completed = False
            st.session_state.move_messages = []
            st.rerun()
    st.stop()

player = st.session_state.current_player

# 🎲 CONTROLS (CENTERED)
c1, c2, c3 = st.columns([1, 2, 1])

with c2:
    if player == "P1":
        if not st.session_state.turn_completed:
            if st.button("Roll Dice (P1's Turn) 🎲", use_container_width=True):
                roll = roll_dice()
                st.session_state.move_messages.append(f"You rolled a {roll} 🎲")

                new_pos = st.session_state.positions[player] + roll
                if new_pos <= 100:
                    st.session_state.positions[player] = new_pos
                    if new_pos in ladders:
                        st.session_state.move_messages.append("Ladder! Climb up! 🎉")
                        handle_snake_ladder(player, new_pos, ladders[new_pos])
                        st.session_state.positions[player] = ladders[new_pos]
                    elif new_pos in snakes:
                        st.session_state.move_messages.append("Snake! Slide down! 🐍")
                        handle_snake_ladder(player, new_pos, snakes[new_pos])
                        st.session_state.positions[player] = snakes[new_pos]
                else:
                    st.session_state.move_messages.append(
                        f"Overshot! Need {100 - st.session_state.positions[player]} more."
                    )

                st.session_state.turn_completed = True
                if st.session_state.positions[player] == 100:
                    st.session_state.game_over = True
                    st.session_state.move_messages.append("P1 Wins! 🏆🎉")
                st.rerun()
        else:
            if st.button("Continue to P2's Turn", use_container_width=True):
                st.session_state.current_player = "P2"
                st.session_state.turn_completed = False
                st.rerun()

    else:
        if not st.session_state.turn_completed:
            st.info("Computer's turn... 🤖")
            time.sleep(1)

            roll = roll_dice()
            st.session_state.move_messages.append(f"Computer rolled a {roll} 🎲")

            new_pos = st.session_state.positions[player] + roll
            if new_pos <= 100:
                st.session_state.positions[player] = new_pos
                if new_pos in ladders:
                    st.session_state.move_messages.append("Computer climbs ladder! 🎉")
                    handle_snake_ladder(player, new_pos, ladders[new_pos])
                    st.session_state.positions[player] = ladders[new_pos]
                elif new_pos in snakes:
                    st.session_state.move_messages.append("Computer slides down snake! 🐍")
                    handle_snake_ladder(player, new_pos, snakes[new_pos])
                    st.session_state.positions[player] = snakes[new_pos]
            else:
                st.session_state.move_messages.append(
                    f"Computer overshot! Needs {100 - st.session_state.positions[player]} more."
                )

            st.session_state.turn_completed = True
            if st.session_state.positions[player] == 100:
                st.session_state.game_over = True
                st.session_state.move_messages.append("P2 Wins! 🏆🎉")
            st.rerun()
        else:
            if st.button("Continue to P1's Turn", use_container_width=True):
                st.session_state.current_player = "P1"
                st.session_state.turn_completed = False
                st.rerun()

# 🐍🪜 Board + Start Zone
display_board()
display_start_zone()

# 📜 GAME LOG (BOTTOM)
st.markdown("---")
st.markdown("### 📜 Game Log")
for msg in st.session_state.move_messages:
    st.write(msg)
