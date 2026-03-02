from pathlib import Path

from pypdf import PdfReader, PdfWriter


def extract_useful_pages(
    input_path: str | Path,
    output_path: str | Path,
    exclude_ranges: list[tuple[int, int]],
) -> None:
    """
    PDF 에서 지정한 페이지

    Args:
        input_path: 원본 PDF 경로
        output_path: 저장할 PDF 경로
        exclude_ranges: 제외할 (시작,끝 페이지) 구간 리스트
    """
    input_path = Path(input_path)
    output_path = Path(output_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    # 1. 제외할 페이지 번호들을 0-index 기반의 Set 으로 만듬
    pages_to_exclude = set[int] = set()
    for start, end in exclude_ranges:
        for i in range(start - 1, end):
            pages_to_exclude.add(i)

    # 2. 전체 페이지를 순회하며 제외 목록에 없는 페이지만 추가합니다.
    total_pages = len(reader.pages)
    for i in range(total_pages):
        if i not in pages_to_exclude:
            writer.add_page(reader.pages[i])

    # 3. 새로운 PDF 파일로 저장.
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    kept = total_pages - len(pages_to_exclude)
    print(f"총 {total_pages} 페이지 중 {len(pages_to_exclude)}")
    print(f"저장된 파일: {output_path} (총 {kept}페이지)")


# ===== 실행 예시 =====
if __name__ == "__main__":
    # 프로젝트 루트 기준: app/document_parser/data/terms/ 원본, output/ 결과 저장
    base = Path(__file__).resolve().parent
    input_pdf = base / "data" / "terms" / "Hi2301_Direct_Medical_Indemnity_Plan.pdf"
    output_pdf = base / "output" / "Hi2301_Direct_Medical_Indemnity_Plan_보상만.pdf"

    # 제외할 페이지 구간 (1-based, 끝 페이지 포함). 계약 내용 등 보상 외 구간을 넣으세요.
    ranges_to_exclude = [
        (9, 27),
        (45, 65),
        # 필요하면 구간 추가
    ]

    extract_useful_pages(input_pdf, output_pdf, ranges_to_exclude)
