"""
OMNIGENIUS - Module 2: Affiliate Swarm
Finds trending products, generates landing pages, prepares for Reddit posting
Uses Tavily for trending product research
"""

import os
import json
from datetime import datetime
from typing import List, Dict
import random

# Product categories to target
TRENDING_CATEGORIES = [
    "tech gadgets",
    "home improvement",
    "fitness equipment",
    "pet products",
    "beauty accessories",
    "gaming accessories"
]


class AffiliateSwarm:
    def __init__(self, output_dir: str = None):
        self.output_dir = output_dir or "PRODUCTS/OmniGenius/affiliates"
        self.products = []
        self.landing_pages = []
        os.makedirs(self.output_dir, exist_ok=True)
        
    def find_trending_products(self, category: str = None) -> List[Dict]:
        """Find trending products using Tavily/web search"""
        products = []
        
        try:
            from web_search import web_search
            
            # Search for trending products
            query = f"trending products {category or 'best sellers'} 2024 2025"
            results = web_search(query=query, count=5)
            
            if results:
                for item in results:
                    products.append({
                        "name": item.get("title", "Unknown Product"),
                        "description": item.get("snippet", "")[:200],
                        "url": item.get("url", ""),
                        "category": category or "general",
                        "found_at": datetime.now().isoformat()
                    })
                    
        except Exception as e:
            print(f"[AffiliateSwarm] Search error: {e}")
            # Fallback demo products
            products = self._demo_products()
            
        self.products = products
        print(f"[AffiliateSwarm] Found {len(products)} trending products")
        return products
    
    def _demo_products(self) -> List[Dict]:
        """Demo products when search fails"""
        return [
            {"name": "Smart Home Hub Pro", "description": "AI-powered home automation device", "category": "tech"},
            {"name": "EcoFitness Resistance Bands", "description": "Sustainable workout bands", "category": "fitness"},
            {"name": "PetFeeder Smart", "description": "Automatic pet feeding with camera", "category": "pets"},
        ]
    
    def generate_landing_page(self, product: Dict) -> str:
        """Generate a landing page HTML for a product"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{product['name']} - Best {product['category'].title()} Product</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; min-height: 100vh; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 40px 20px; }}
        .hero {{ text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #667eea, #764ba2); border-radius: 20px; margin-bottom: 40px; }}
        .hero h1 {{ font-size: 3em; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .hero p {{ font-size: 1.5em; opacity: 0.9; }}
        .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 40px 0; }}
        .feature {{ background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; text-align: center; }}
        .feature h3 {{ color: #667eea; margin-bottom: 15px; font-size: 1.3em; }}
        .cta {{ text-align: center; padding: 40px; }}
        .cta button {{ background: #ff6b6b; color: white; border: none; padding: 20px 50px; font-size: 1.3em; border-radius: 50px; cursor: pointer; transition: transform 0.3s; }}
        .cta button:hover {{ transform: scale(1.05); box-shadow: 0 10px 30px rgba(255,107,107,0.4); }}
        .footer {{ text-align: center; padding: 40px; opacity: 0.6; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>🔥 {product['name']} 🔥</h1>
            <p>{product.get('description', 'The ultimate solution for your needs')}</p>
        </div>
        
        <div class="features">
            <div class="feature">
                <h3>⭐ Premium Quality</h3>
                <p>Built with the finest materials for lasting performance</p>
            </div>
            <div class="feature">
                <h3>🚀 Fast Shipping</h3>
                <p>Get delivered within 2-3 business days</p>
            </div>
            <div class="feature">
                <h3>💯 Best Price</h3>
                <p>Unbeatable value for money - Limited time offer!</p>
            </div>
        </div>
        
        <div class="cta">
            <button onclick="window.open('{product.get('url', '#')}', '_blank')">
                Buy Now ⏩
            </button>
        </div>
        
        <div class="footer">
            <p>© 2025 {product['name']} | As an Amazon Associate we earn from qualifying purchases</p>
        </div>
    </div>
</body>
</html>"""
        
        # Save the landing page
        safe_name = product['name'].lower().replace(' ', '_')
        filename = f"landing_{safe_name}_{datetime.now().strftime('%Y%m%d')}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(html)
            
        self.landing_pages.append({"product": product, "file": filepath})
        print(f"[AffiliateSwarm] Generated landing page: {filename}")
        
        return filepath
    
    def prepare_reddit_post(self, product: Dict) -> Dict:
        """Prepare a Reddit-ready post"""
        
        post = {
            "title": f"🔥 Found: {product['name']} - Must have!",
            "body": f"""**{product['name']}**

{product.get('description', '')}

**Why you need this:**
✅ Premium quality
✅ Fast shipping  
✅ Best price on the market

**Check it out:** {product.get('url', '')}

*I'm not affiliated, just sharing what I found!*

---
^(As an Amazon Associate I earn from qualifying purchases)""",
            "subreddit": self._get_relevant_subreddit(product.get('category', '')),
            "product": product,
            "created_at": datetime.now().isoformat()
        }
        
        # Save post draft
        draft_file = os.path.join(self.output_dir, f"reddit_draft_{product['name'].lower().replace(' ', '_')}.json")
        with open(draft_file, 'w') as f:
            json.dump(post, f, indent=2)
            
        print(f"[AffiliateSwarm] Prepared Reddit post for r/{post['subreddit']}")
        return post
    
    def _get_relevant_subreddit(self, category: str) -> str:
        """Get relevant subreddit for product category"""
        subreddits = {
            "tech": "gadgets",
            "fitness": "fitness",
            "pets": "pets",
            "home": "HomeImprovement",
            "beauty": "beauty",
            "gaming": "gaming"
        }
        return subreddits.get(category.lower(), "amazonfinds")
    
    def run(self, categories: List[str] = None):
        """Run full affiliate swarm"""
        if categories is None:
            categories = TRENDING_CATEGORIES[:2]  # Limit for demo
            
        print(f"[AffiliateSwarm] Starting affiliate campaign for {len(categories)} categories...")
        
        for category in categories:
            print(f"  Scanning: {category}")
            products = self.find_trending_products(category)
            
            for product in products[:3]:  # Top 3 products
                self.generate_landing_page(product)
                self.prepare_reddit_post(product)
                
        print(f"[AffiliateSwarm] Campaign complete. Generated {len(self.landing_pages)} landing pages")
        return {
            "products": self.products,
            "landing_pages": self.landing_pages
        }


if __name__ == "__main__":
    swarm = AffiliateSwarm()
    swarm.run()
