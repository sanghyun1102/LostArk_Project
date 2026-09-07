# LostArk Project Development Log

Lost Ark Open API를 활용한 캐릭터 분석 및 성장 추천 서비스 개발 기록입니다.

---

## 2026-09-07

### 개발 환경 구축

- VS Code 프로젝트 생성
- Python 가상환경 `.venv` 생성
- `requests`, `python-dotenv` 설치
- `.env`를 이용한 Lost Ark Open API Key 관리
- `.gitignore` 설정
- GitHub Repository 연결

### Lost Ark Open API 연동

- Lost Ark Open API 캐릭터 조회 테스트
- 캐릭터 정보 정상 응답 확인
- API 응답 데이터를 JSON 파일로 저장
- `data/raw` 디렉터리에 원본 데이터 저장
- 원본 데이터는 Git 추적 대상에서 제외

### ArmoryProfile 분석

캐릭터 기본 정보를 파싱하도록 구현.

추출 항목:

- 캐릭터명
- 서버
- 클래스
- 캐릭터 레벨
- 아이템 레벨
- 전투력
- 치명
- 특화
- 신속
- 공격력
- 최대 생명력

### ArmoryEquipment 분석

#### 무기

추출 항목:

- 강화 단계
- 아이템 레벨
- 품질
- 무기 공격력
- 추가 피해

#### 방어구

5개 부위의 정보를 파싱하도록 구현.

- 투구
- 상의
- 하의
- 장갑
- 어깨

추출 항목:

- 강화 단계
- 아이템 레벨
- 품질

추가로 평균 방어구 강화 단계와 평균 품질 계산.

### Skill Gem 분석

아크그리드의 Gem과 혼동되지 않도록 기존 보석 관련 변수명을 `skill_gem`으로 통일.

추출 항목:

- 슬롯
- 보석 종류 (겁화 / 작열)
- 보석 레벨
- 등급
- 적용 스킬
- 보석 효과
- 기본 공격력 증가 효과

추가 계산:

- 스킬 보석 개수
- 평균 스킬 보석 레벨

### ArmoryEngraving 분석

`ArkPassiveEffects`에서 현재 사용 중인 각인 정보 확인.

확인 항목:

- 각인 이름
- 각인 레벨
- 등급
- 어빌리티 스톤 레벨
- 각인 설명

### 다음 작업

- `parse_engravings()` 최종 확인
- `ArkPassive` 데이터 구조 분석
- 아크 패시브 데이터 파싱
- 아크그리드 데이터 분석