# ER Plot: 블랙 서바이벌 랭크 게임 통계 시각화 도구
English version of README is [here](README_eng.md).

![대체 텍스트](assets/image.png)

이 저장소는 Eternal Return Black Survival의 랭크 게임 내 캐릭터 분석을 위한 비상업적 프로젝트입니다. dak.gg에서 가져온 데이터를 활용하여, 이 시스템은 게임 후 분석을 상호작용적으로 수행할 수 있게 해줍니다. 이 프로젝트는 [Nimble Neuron](https://nimbleneuron.com/) 또는 [dak.gg](https://dak.gg/)와는 관련이 없으며 그들에 의해 승인되거나 지지받지 않습니다.

## 설명

이 프로젝트의 목적은 픽률, 승률, Top 3 빈도 및 RP 획득량과 같은 다양한 성능 지표를 기반으로 캐릭터의 시각적 및 통계적 분석을 위한 상호작용 플랫폼을 제공하는 것입니다.

주요 특징:

- 픽률, 승률, Top 3 완성도 및 RP 획득량을 기준으로 캐릭터를 시각적으로 비교하는 상호작용형 플롯.
- 데이터를 새롭게 유지하기 위해 3시간마다 자동 업데이트. 데이터 소스는 [dak.gg](https://dak.gg/er/statistics)에서 가져옴.
- 다른 게임 버전, 티어 및 포지션에 걸쳐 비교 분석.
- 사용자가 특히 관심 있는 캐릭터 그룹을 강조할 수 있는 사용자 정의 옵션.
- 포인트 호버링, 확대/축소 등 plotly의 모든 기능을 활용하여 향상된 데이터 시각화.
- 활동 중인 (추정) 세션 수 추적.

## 설치

```bash
# 저장소를 복제합니다.
git clone https://github.com/mikigom/ER_plot

# 저장소 디렉토리로 이동합니다.
cd ER_plot

# 필요한 종속성을 설치합니다.
pip install -r requirements.txt

sudo apt install chromium-chromedriver
# 만약 최신 버전의 chromium-chromedriver의 사용이 불가능하다면
sudo apt-get install firefox
```

## 사용법

```bash
# 애플리케이션을 실행합니다.
python run.py
```

이 명령어는 상호작용 데이터 시각화 인터페이스를 제공하는 웹 서비스를 시작합니다.

## 기여하기

기여를 환영합니다. 저장소를 포크하고 제안하는 변경 사항을 풀 리퀘스트로 제출해 주세요.
기능 요청 및 버그 리포트도 환영하지만, 제 개인 사정으로 대부분 즉각적인 반영이 힘들 수 있음을 양해 바랍니다.
만약 기능 요청 및 버그 리포트를 원한다면, 이슈로서 남겨주세요.

## 크레딧

이 도구는 ER의 유저들을 위해 [@MikiBear_](https://twitter.com/MikiBear_)에 의해 만들어졌습니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 공개되어 있습니다 - 자세한 내용은 LICENSE 파일을 참조해 주세요.
