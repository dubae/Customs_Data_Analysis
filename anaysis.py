import pandas as pd

# CSV 파일 읽기
file_path = 'incomeoutcome.csv'
data = pd.read_csv(file_path)

# 특정 HS 코드에 대해 거래한 국가들을 정렬하는 함수
def sort_by_hs_code(hs_code):
    # HS 코드로 필터링하고, 수출 중량과 수입 중량이 0이 아닌 데이터만 선택
    filtered_data = data[(data['HS코드'] == hs_code) & (data['수출 중량'] > 0) & (data['수입 중량'] > 0)]
    
    # # 수출 금액과 수입 금액을 달러로 변환 (1000을 곱함)
    # filtered_data['수출 금액'] = filtered_data['수출 금액'] * 1000
    # filtered_data['수입 금액'] = filtered_data['수입 금액'] * 1000
    
    # "수출 금액/수출 중량" 계산
    export_value_per_weight = filtered_data['수출 금액']*1000 / filtered_data['수출 중량']
    # "수입 금액/수입 중량" 계산
    import_value_per_weight = filtered_data['수입 금액']*1000 / filtered_data['수입 중량']
    
    # 정렬 인덱스 생성
    sorted_export_indices = export_value_per_weight.argsort()[::-1]  # 내림차순 정렬
    sorted_import_indices = import_value_per_weight.argsort()  # 오름차순 정렬
    
    # 정렬된 데이터 반환 (원본 데이터프레임에서 인덱스로 접근)
    sorted_export_data = filtered_data.iloc[sorted_export_indices]
    sorted_import_data = filtered_data.iloc[sorted_import_indices]
    return sorted_export_data, export_value_per_weight.iloc[sorted_export_indices], sorted_import_data, import_value_per_weight.iloc[sorted_import_indices]

# 사용자가 입력한 HS 코드를 받아서 정렬된 데이터를 반환
hs_code_input = 3  # 예시로 "03" 코드를 사용
sorted_export_data, sorted_export_value_per_weight, sorted_import_data, sorted_import_value_per_weight = sort_by_hs_code(hs_code_input)

# 출력 형식 지정 및 출력
print(f"수출 기준 [순위] [국가명] [수출 중량(kg)] [수출 금액($)] [수출 단가($/kg)]")
for i, (index, row) in enumerate(sorted_export_data.iterrows(), start=1):
    print(f"[{i}] [{row['국가']}] [{row['수출 중량']:.1f}kg] [${1000*row['수출 금액']:,}] [${sorted_export_value_per_weight[index]:.6f}/kg]")

print("\n수입 기준 [순위] [국가명] [수입 중량(kg)] [수입 금액($)] [수입 단가($/kg)]")
for i, (index, row) in enumerate(sorted_import_data.iterrows(), start=1):
    print(f"[{i}] [{row['국가']}] [{row['수입 중량']:.1f}kg] [${1000*row['수입 금액']:,}] [${sorted_import_value_per_weight[index]:.6f}/kg]")
