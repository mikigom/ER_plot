url_mapping = {}
url_mapping[('platinum_plus', 'prevPatch')] = "https://dak.gg/er/statistics?tier=platinum_plus&period=prevPatch"
url_mapping[('platinum_plus', 'currentPatch')] = "https://dak.gg/er/statistics?tier=platinum_plus&period=currentPatch"
url_mapping[('platinum_plus', '3day')] = "https://dak.gg/er/statistics?tier=platinum_plus&period=3day"
url_mapping[('platinum_plus', '7day')] = "https://dak.gg/er/statistics?tier=platinum_plus&period=7day"
url_mapping[('diamond_plus', 'prevPatch')] = "https://dak.gg/er/statistics?tier=diamond_plus&period=prevPatch"
url_mapping[('diamond_plus', 'currentPatch')] = "https://dak.gg/er/statistics?tier=diamond_plus&period=currentPatch"
url_mapping[('diamond_plus', '3day')] = "https://dak.gg/er/statistics?tier=diamond_plus&period=3day"
url_mapping[('diamond_plus', '7day')] = "https://dak.gg/er/statistics?tier=diamond_plus&period=7day"
url_mapping[('in_1000', 'prevPatch')] = "https://dak.gg/er/statistics?position=all&tier=in1000&period=prevPatch"
url_mapping[('in_1000', 'currentPatch')] = "https://dak.gg/er/statistics?position=all&tier=in1000&period=currentPatch"
url_mapping[('in_1000', '3day')] = "https://dak.gg/er/statistics?position=all&tier=in1000&period=3day"
url_mapping[('in_1000', '7day')] = "https://dak.gg/er/statistics?position=all&tier=in1000&period=7day"

default_roles_mapping = {}
default_roles_mapping['Melee Carry'] = [
    "도끼 아비게일",
    "방망이 루크",
    "글러브 리 다이린",
    "레이피어 키아라",
    "양손검 에이든",
    "VF의수 에키온",
    "레이피어 피오라",
    "단검 쇼우",
    "창 쇼우",
    "창 펠릭스",
    "레이피어 카밀로",
    "채찍 라우라",
    "쌍절곤 리 다이린",
    "단검 이안",
    "쌍검 카밀로",
    "양손검 피오라",
    "창 피오라",
    "망치 매그너스",
    "방망이 매그너스",
    "양손검 데비&마를렌",
    "쌍검 유키",
    "글러브 니키",
    "레이피어 엘레나",
    "글러브 현우",
    "톤파 아이작",
    "방망이 수아",
    "양손검 유키",
    "쌍검 재키",
    "아르카나 바냐",
    "쌍절곤 피올로",
    "톤파 알렉스",
    "글러브 레온",
    "양손검 재키",
    "톤파 현우",
    "도끼 재키",
    "망치 수아",
    "단검 재키",
    "톤파 얀",
    "글러브 얀"
] # 17

default_roles_mapping['Skill Ranged Carry'] = [
    "돌격소총 헤이즈",
    "권총 아야",
    "암기 시셀라",
    "아르카나 아르다",
    "투척 이렘",
    "암기 혜진",
    "투척 아드리아나",
    "권총 아이솔",
    "아르카나 엠마",
    "투척 이바",
    "활 혜진",
    "투척 셀린",
    "아르카나 아디나",
    "저격총 테오도르",
    "암기 타지아",
    "카메라 나타폰",
    "권총 제니",
    "석궁 칼라",
    "방망이 아델라",
    "저격총 아야",
    "암기 자히르",
    "암기 엠마",
    "활 나딘",
    "투척 시셀라",
    "투척 자히르",
    "레이피어 아델라",
    "아르카나 비앙카",
    "방망이 띠아",
    "권총 실비아",
    "방망이 바바라",
    "톤파 알렉스"
] # 26

default_roles_mapping['Attack Ranged Carry'] = [
    "활 리오",
    "권총 로지",
    "돌격소총 아야",
    "돌격소총 아이솔",
    "저격총 버니스",
    "암기 클로에",
    "기타 하트",
    "투척 윌리엄",
    "석궁 나딘",
    "카메라 마르티나",
    "톤파 알렉스"
] # 10

default_roles_mapping['Tanker'] = [
    "채찍 레녹스",
    "레이피어 엘레나",
    "글러브 알론소",
    "도끼 마커스",
    "망치 일레븐",
    "채찍 마이",
    "도끼 에스텔",
    "망치 마커스"
]

default_roles_mapping['Assassin'] = [
    "쌍검 캐시",
    "단검 쇼이치",
    "단검 다니엘",
    "단검 캐시"
]

default_roles_mapping['Supporter'] = [
    "채찍 마이",
    "글러브 레온",
    "저격총 테오도르",
    "기타 프리야",
    "아르카나 요한",
    "톤파 레온",
    "권총 레니"
]

def custom_sort_korean(lst):
    def sort_key(s):
        parts = s.split(' ')
        # Join all parts from the second one if there are more than two parts
        return ''.join(parts[1:]) if len(parts) > 1 else ''

    return sorted(lst, key=sort_key)

default_roles_mapping['Reference'] = []
for key, value in default_roles_mapping.items():
    default_roles_mapping['Reference'].extend(value)
default_roles_mapping['Reference'] = custom_sort_korean(list(set(default_roles_mapping['Reference'])))

default_roles_mapping['User Defined'] = []

role_translation = {}
role_translation['Whole'] = '전체'
role_translation['Melee Carry'] = '근거리 딜러'
role_translation['Skill Ranged Carry'] = '스킬 원거리 딜러'
role_translation['Attack Ranged Carry'] = '평타 원거리 딜러'
role_translation['Tanker'] = '탱커'
role_translation['Assassin'] = '암살자'
role_translation['Supporter'] = '서포터'
role_translation['User Defined'] = '유저 정의'

# Define some style settings
GLOBAL_FONT_FAMILY = "Helvetica Neue, Helvetica, Arial, sans-serif"
PRIMARY_COLOR = "#007BFF"
SECONDARY_COLOR = "#6c757d"
BACKGROUND_COLOR = "#f8f9fa"
TEXT_COLOR = "#212529"
