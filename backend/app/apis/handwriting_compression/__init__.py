from fastapi import APIRouter

# Create a router with a prefix that matches both hyphenated and underscore paths
router = APIRouter(tags=["handwriting"])  # Tags don't affect routing, just for documentation

# This API has been superseded by hwx_compression API
# This stub remains to avoid breaking existing routes
