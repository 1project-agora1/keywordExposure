import json
import os
from datetime import datetime
from tqdm import tqdm

class KeywordMonitor:
    def __init__(self, scraper, config_path, results_path):
        self.scraper = scraper
        self.config_path = config_path
        self.results_path = results_path
        
    def load_keywords(self):
        """키워드 및 URL 설정 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"keywords": []}
        
    def save_results(self, results):
        """결과 저장"""
        # 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(self.results_path), exist_ok=True)
        
        with open(self.results_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
    def check_url_in_results(self, url, search_urls):
        """URL이 검색 결과에 있는지 확인"""
        # URL 정규화 및 비교 로직을 향상시킬 수 있음
        for search_url in search_urls:
            if url in search_url or search_url in url:
                return True
        return False
        
    def monitor_keywords(self, pages_to_check=1):  # 기본값을 1로 변경
        """모든 키워드 모니터링 - 첫 페이지만 검색"""
        config = self.load_keywords()
        results = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "results": []
        }
        
        print(f"총 {len(config['keywords'])} 개의 키워드를 모니터링합니다...")
        
        for item in tqdm(config['keywords'], desc="키워드 검색 중"):
            keyword = item["keyword"]
            target_urls = item["urls"]
            
            print(f"\n키워드 '{keyword}' 검색 중...")
            all_search_urls = []
            
            # 첫 페이지만 검색 (pages_to_check=1)
            print(f"  페이지 1 검색 중...")
            soup = self.scraper.get_search_results(keyword, page=1)
            if soup:
                page_urls = self.scraper.extract_urls(soup)
                all_search_urls.extend(page_urls)
                print(f"  페이지 1에서 {len(page_urls)}개의 URL을 찾았습니다.")
            
            # 각 URL 노출 여부 확인
            url_results = []
            for url in target_urls:
                is_exposed = self.check_url_in_results(url, all_search_urls)
                status = "노출" if is_exposed else "미노출"
                print(f"  URL '{url}' - {status}")
                
                url_results.append({
                    "url": url,
                    "is_exposed": is_exposed
                })
                
            keyword_result = {
                "keyword": keyword,
                "urls": url_results
            }
            
            results["results"].append(keyword_result)
            
        self.save_results(results)
        print(f"\n모니터링 결과가 {self.results_path}에 저장되었습니다.")
        return results