from datetime import datetime

import pytz
import streamlit as st
import streamlit_calendar as st_calendar

st.set_page_config(layout="wide")
st.markdown("""
# Meeting Time Scheduler

## How to use

1. Select your preferred secondary time zone from the dropdown menu.
2. Choose the desired date range in the calendar panel.
3. The selected date range will be displayed in the text area below.
4. If you want to display the time in both JST and the selected secondary time zone, keep the "Use Secondary Time Zone" checkbox checked. If you only want to display the time in JST, uncheck the box.
5. The selected date ranges will be accumulated in the text area. You can copy the text and use it in your communication.

Note: The calendar is set to display in week view by default. You can change the view using the buttons at the top of the calendar.
            
## Made by

Hiroyuki Odake, All rights reserved (2024)

## License

MIT
""")

# タイムゾーンのリストを作成
timezones = pytz.common_timezones
timezone_options = [
    f"(GMT{pytz.timezone(tz).localize(datetime.now()).strftime('%z')}) {tz} ({pytz.timezone(tz).tzname(datetime.now())})"
    for tz in timezones
]

# オプションを指定
options = {
    "initialView": "timeGridWeek",
    "selectable": True,
    "selectMirror": True,
    "unselectAuto": False,
    "slotMinTime": "05:00:00",  # 表示開始時間をAM 5:00に設定
    "slotMaxTime": "24:00:00",  # 表示終了時間をPM 12:00に設定
}

# 選択範囲を保持するセッション状態
if "selected_ranges" not in st.session_state:
    st.session_state.selected_ranges = []

# ページレイアウトを幅広に設定


# レイアウトを2列に分割
col1, col2 = st.columns([3, 1])

# 左側にカレンダーを表示
with col1:
    calendar_status = st_calendar.calendar(options=options)

# 右側にセカンダリタイムゾーンの選択メニューと選択範囲の表示を配置
with col2:
    selected_timezone = st.selectbox("セカンダリタイムゾーンを選択", timezone_options)
    secondary_timezone = pytz.timezone(
        selected_timezone.split(")")[1].split("(")[0].strip()
    )

    # チェックボックスを追加
    use_secondary_timezone = st.checkbox("Use Secondary Time Zone", value=True)

    # 選択範囲を取得
    if calendar_status and "select" in calendar_status:
        selected_range = calendar_status["select"]
        st.session_state.selected_ranges.append(selected_range)

    # 選択範囲を表示
    for range in st.session_state.selected_ranges:
        # start_date と end_date をパース
        start_date = datetime.fromisoformat(range["start"])
        end_date = datetime.fromisoformat(range["end"])

        # datetime がすでにタイムゾーン情報を持っているかどうかをチェックし、必要に応じて変換
        if start_date.tzinfo is None and end_date.tzinfo is None:
            # タイムゾーン情報がない場合、UTCとして扱い、JSTに変換
            utc_tz = pytz.timezone("UTC")
            start_date = utc_tz.localize(start_date)
            end_date = utc_tz.localize(end_date)
        else:
            # タイムゾーン情報がすでにある場合、変換のみを行う
            start_date = start_date.astimezone(pytz.timezone("UTC"))
            end_date = end_date.astimezone(pytz.timezone("UTC"))

    # テキストボックスを初期化
    if "info_text" not in st.session_state:
        st.session_state["info_text"] = ""

    # JSTとセカンダリタイムゾーンの時間を表示
    jst_start = start_date.astimezone(pytz.timezone("Asia/Tokyo"))
    jst_end = end_date.astimezone(pytz.timezone("Asia/Tokyo"))

    if use_secondary_timezone:
        secondary_start = jst_start.astimezone(secondary_timezone)
        secondary_end = jst_end.astimezone(secondary_timezone)

        # タイムゾーン名を取得
        jst_tz_name = "JST"
        secondary_tz_name = secondary_start.tzname()

        # 12時間制の時刻表記を取得
        secondary_start_time = secondary_start.strftime("%-I:%M %p")
        secondary_end_time = secondary_end.strftime("%-I:%M %p")
        jst_start_time = jst_start.strftime("%-I:%M %p")
        jst_end_time = jst_end.strftime("%-I:%M %p")

        # 選択範囲の情報を作成
        range_info = f"{secondary_start.strftime('%B %-d')}{'st' if secondary_start.day == 1 else ('nd' if secondary_start.day == 2 else ('rd' if secondary_start.day == 3 else 'th'))}, {secondary_tz_name} {secondary_start_time}-{secondary_end_time} ({jst_start.strftime('%B %-d')}{'st' if jst_start.day == 1 else ('nd' if jst_start.day == 2 else ('rd' if jst_start.day == 3 else 'th'))}, {jst_tz_name} {jst_start_time} - {jst_end_time})"
    else:
        # 選択範囲の情報を作成（日本語表記のみ）
        range_info = (
            f"{jst_start.strftime('%Y年%m月%d日 %H:%M')} - {jst_end.strftime('%H:%M')}"
        )

    # 選択範囲の情報をスタックして表示
    st.session_state["info_text"] += range_info + "\n"
    st.text_area("Selected Ranges", value=st.session_state["info_text"], height=200)
