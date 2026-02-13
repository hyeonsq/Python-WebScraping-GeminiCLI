
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from loguru import logger
import re
import io

# Matplotlib 한글 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 로거 설정
logger.add("yes24_eda.log", rotation="500 MB")

def clean_column_names(df):
    """ 데이터프레임의 컬럼명을 정리합니다. """
    cols = df.columns
    new_cols = []
    for col in cols:
        new_col = re.sub(r'[^A-Za-z0-9_]+', '', col)
        new_cols.append(new_col)
    df.columns = new_cols
    return df

@logger.catch
def main():
    # 1. 데이터 불러오기
    try:
        df = pd.read_csv('C:/webscraping_gemini/yes24/data/yes24_ai.csv')
        logger.info("CSV 파일을 성공적으로 불러왔습니다.")
    except FileNotFoundError:
        logger.error("CSV 파일을 찾을 수 없습니다.")
        return

    df = clean_column_names(df)

    # 데이터 저장 경로 설정
    image_dir = 'C:/webscraping_gemini/yes24/data/'

    # "데이터 정보" 섹션을 위한 StringIO 버퍼
    buffer = io.StringIO()
    df.info(buf=buffer)
    df_info_str = buffer.getvalue()
    
    # 기초 통계
    df_describe_str = df.describe().to_markdown()

    # 3. 데이터 시각화
    # 가격 분포
    plt.figure(figsize=(10, 5))
    sns.histplot(df['Original_Price'], kde=True, label='Original Price')
    sns.histplot(df['Discounted_Price'], kde=True, label='Discounted Price', color='orange')
    plt.title('가격 분포')
    plt.xlabel('가격')
    plt.ylabel('도서 수')
    plt.legend()
    price_dist_path = f"{image_dir}price_distribution.png"
    plt.savefig(price_dist_path)
    plt.close()
    logger.info(f"가격 분포 그래프를 {price_dist_path}에 저장했습니다.")

    # 출판사별 도서 수
    plt.figure(figsize=(12, 6))
    sns.countplot(y='Publisher', data=df, order = df['Publisher'].value_counts().index)
    plt.title('출판사별 도서 수')
    plt.xlabel('도서 수')
    plt.ylabel('출판사')
    publisher_books_path = f"{image_dir}publisher_books.png"
    plt.savefig(publisher_books_path)
    plt.close()
    logger.info(f"출판사별 도서 수 그래프를 {publisher_books_path}에 저장했습니다.")

    # 평점 분포
    plt.figure(figsize=(10, 5))
    sns.histplot(df['Rating'], kde=True)
    plt.title('평점 분포')
    plt.xlabel('평점')
    plt.ylabel('도서 수')
    rating_dist_path = f"{image_dir}rating_distribution.png"
    plt.savefig(rating_dist_path)
    plt.close()
    logger.info(f"평점 분포 그래프를 {rating_dist_path}에 저장했습니다.")

    # 판매지수와 평점 관계
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Sales_Index', y='Rating', data=df)
    plt.title('판매지수와 평점 관계')
    plt.xlabel('판매지수')
    plt.ylabel('평점')
    sales_rating_path = f"{image_dir}sales_rating.png"
    plt.savefig(sales_rating_path)
    plt.close()
    logger.info(f"판매지수와 평점 관계 그래프를 {sales_rating_path}에 저장했습니다.")

    # 태그 워드클라우드
    # Tags 컬럼의 결측값 처리
    tags_text = ' '.join(df['Tags'].dropna().astype(str).tolist())
    
    # 폰트 경로 설정 (Windows 환경을 가정)
    font_path = 'C:/Windows/Fonts/malgunbd.ttf' # 맑은 고딕 볼드체 (일반 맑은 고딕도 가능)
    
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(tags_text)
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('태그 워드클라우드')
    wordcloud_path = f"{image_dir}tags_wordcloud.png"
    plt.savefig(wordcloud_path)
    plt.close()
    logger.info(f"태그 워드클라우드를 {wordcloud_path}에 저장했습니다.")
    
    # 4. 마크다운 파일 내용 생성 및 업데이트
    md_content = f"""# YES24 AI 도서 데이터 분석

## 1. 데이터 개요

### 데이터 일부

{df.head().to_markdown(index=False)}

### 데이터 정보

총 12개의 컬럼과 25개의 행으로 구성되어 있습니다. 각 컬럼의 데이터 타입과 결측치 여부는 다음과 같습니다.

```
{df_info_str}
```

`Tags` 컬럼에 2개의 결측치가 존재하며, `Original_Price`, `Discounted_Price`, `Sales_Index`, `Review_Count`, `Rating` 컬럼은 수치형 데이터로 구성되어 있습니다.

### 기초 통계

```
{df_describe_str}
```

## 2. 데이터 시각화

### 가격 분포

원본 가격과 할인된 가격의 분포를 보여주는 히스토그램입니다. 대부분의 도서가 20,000원에서 25,000원 사이에 분포하고 있음을 확인할 수 있습니다.

![가격 분포](./data/price_distribution.png)

### 출판사별 도서 수

각 출판사별로 출간된 도서의 수를 보여주는 막대 그래프입니다. '이지스퍼블리싱'이 가장 많은 AI 관련 도서를 출판했음을 알 수 있습니다.

![출판사별 도서 수](./data/publisher_books.png)

### 평점 분포

도서 평점의 분포를 나타내는 히스토그램입니다. 대부분의 도서가 높은 평점을 유지하고 있으며, 9.5점 이상의 도서가 많습니다.

![평점 분포](./data/rating_distribution.png)

### 판매지수와 평점 관계

판매지수와 평점 간의 관계를 보여주는 산점도입니다. 판매지수가 높은 도서가 반드시 평점도 높지는 않으며, 두 지표 간에 강한 선형 관계는 보이지 않습니다.

![판매지수와 평점 관계](./data/sales_rating.png)

### 태그 워드클라우드

도서 태그를 분석하여 워드클라우드 형태로 시각화한 것입니다. '챗GPT', 'AI', '파이썬', '인공지능'과 같은 키워드가 자주 등장함을 알 수 있습니다.

![태그 워드클라우드](./data/tags_wordcloud.png)
"""
    try:
        with open('C:/webscraping_gemini/yes24/agent_eda_yes24.md', 'w', encoding='utf-8') as f:
            f.write(md_content)
        logger.info("마크다운 파일을 성공적으로 업데이트했습니다.")
    except Exception as e:
        logger.error(f"마크다운 파일 업데이트 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
