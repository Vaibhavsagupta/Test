from fastapi import APIRouter
from app.services.pipeline import extract_leads_pipeline
from app.services.recommender import RecommenderService

router = APIRouter()
recommender = RecommenderService()

@router.get("/search")
def search(q: str, top_k: int = 10, include_nsfw: bool = False):
    """ Task 1: Recommend relevant subreddits based on query. """
    return recommender.search_subreddits(q, top_k, include_nsfw=include_nsfw)

@router.get("/extract-leads")
def extract_leads(url: str):
    """ Task 2: Extract leads and intent from a Reddit post URL. """
    return extract_leads_pipeline(url)

@router.get("/test-live")
def test_live():
    """ 
    Special static test route added to verify pipeline with live data 
    without needing manually provided URLs.
    """
    test_url = "https://www.reddit.com/r/HairTransplants/comments/17dfp3d/who_are_the_best_surgeons_in_thailand_budget_no/"
    return extract_leads_pipeline(test_url)

