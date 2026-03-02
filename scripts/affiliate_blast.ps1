# MONEY ARMY 5 - Affiliate Marketing Blast
# Creates affiliate links and posts for maximum exposure

$LOG_FILE = "$env:USERPROFILE\.openclaw\workspace\logs\affiliate.log"
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\data" | Out-Null

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "`n🎯 AFFILIATE MARKETING BLAST - $timestamp" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Top products to promote
$PRODUCTS = @(
    @{
        Name = "NordVPN"
        Niche = "Privacy/Tech"
        Commission = "$30-$100 per sale"
        Description = "VPN service for online privacy"
        URL = "https://www.nordvpn.com/affiliates"
        PromoPost = @"
🚨 URGENT: Your ISP is selling your browsing data RIGHT NOW!

I just switched to NordVPN and WOW:
✅ No more tracking
✅ Access geo-blocked content
✅ 30 day money-back guarantee

Limited time: 68% OFF + 3 months FREE
👉 [Your affiliate link here]

Protect your privacy today!
"@
    },
    @{
        Name = "Bluehost"
        Niche = "Hosting/Web"
        Commission = "$65-$130 per sale"
        Description = "Web hosting for websites"
        URL = "https://www.bluehost.com/affiliates"
        PromoPost = @"
Starting a blog or website in 2025?

I recommend Bluehost:
✅ $2.95/month (60% off)
✅ Free domain included
✅ WordPress recommended
✅ 24/7 support

Perfect for beginners!
👉 [Your affiliate link]

Start your online business today!
"@
    },
    @{
        Name = "Skillshare"
        Niche = "Education"
        Commission = "$7 per trial"
        Description = "Online learning platform"
        URL = "https://www.skillshare.com/affiliate"
        PromoPost = @"
Learn ANY skill this month for FREE!

Skillshare Premium:
✅ 30,000+ classes
✅ Design, business, tech, cooking
✅ First month FREE
✅ Cancel anytime

I learned [skill] yesterday!
👉 [Your affiliate link]

What will YOU learn today?
"@
    },
    @{
        Name = "Audible"
        Niche = "Books/Entertainment"
        Commission = "$5 per trial"
        Description = "Audiobook platform"
        URL = "https://www.audible.com/affiliates"
        PromoPost = @"
FREE audiobook + 30 days unlimited listening!

Audible Premium Plus:
✅ 1 FREE audiobook (keep forever)
✅ Unlimited Audible originals
✅ Cancel anytime
✅ Works on all devices

I'm listening to [book] right now!
👉 [Your affiliate link]

Try it FREE today!
"@
    },
    @{
        Name = "DoorDash"
        Niche = "Food Delivery"
        Commission = "$5-$20 per referral"
        Description = "Food delivery service"
        URL = "https://www.doordash.com/dasher/apply/"
        PromoPost = @"
Make $500 THIS WEEK delivering food!

DoorDash driver:
✅ $15-$25/hour
✅ Flexible schedule
✅ Get paid instantly
✅ Just need a bike/car

Drivers needed in [your city]!
👉 [Referral link]

Start earning today!
"@
    },
    @{
        Name = "Robinhood"
        Niche = "Finance/Crypto"
        Commission = "$5-$50 per signup"
        Description = "Stock/crypto trading app"
        URL = "https://robinhood.com/us/en/support/articles/invite-friends/"
        PromoPost = @"
Get FREE STOCK when you sign up!

Robinhood:
✅ Commission-free trading
✅ Stocks, ETFs, Crypto
✅ Fractional shares
✅ Get FREE stock (up to $200)

I got [stock name] for free!
👉 [Your referral link]

Start investing today!
"@
    }
)

# Display products
foreach ($prod in $PRODUCTS) {
    Write-Host "`n📦 $($prod.Name)" -ForegroundColor Yellow
    Write-Host "   Niche: $($prod.Niche)" -ForegroundColor White
    Write-Host "   Commission: $($prod.Commission)" -ForegroundColor Green
    Write-Host "   Description: $($prod.Description)" -ForegroundColor Gray
    Write-Host "   URL: $($prod.URL)" -ForegroundColor Blue
    Write-Host "`n   SAMPLE POST:" -ForegroundColor Magenta
    Write-Host "$($prod.PromoPost)" -ForegroundColor White
    Write-Host "   ---" -ForegroundColor Gray
}

# Social media post templates
$TEMPLATES = @(
    "Just discovered [PRODUCT] and WOW! Saved me so much time/money. Highly recommend! 👉 [link]",
    "Game changer! I've been using [PRODUCT] for [time] and it's incredible. Try it: [link]",
    "PRO TIP: Stop wasting money on [expensive alternative]. Use [PRODUCT] instead! [link]",
    "Finally, a [solution] that actually works! [PRODUCT] is legit. Check it out: [link]",
    "Friendly reminder that [PRODUCT] exists and it's AMAZING. You're welcome! [link]"
)

Write-Host "`n📝 COPY-PASTE TEMPLATES:" -ForegroundColor Green
foreach ($template in $TEMPLATES) {
    Write-Host "   $template" -ForegroundColor White
}

# Where to post
Write-Host "`n🌐 POSTING LOCATIONS:" -ForegroundColor Cyan
Write-Host "   Reddit: r/beermoney, r/sidehustle, r/passive_income" -ForegroundColor White
Write-Host "   Twitter/X: Daily threads, retweet with comments" -ForegroundColor White
Write-Host "   Facebook: Groups in your niche, personal posts" -ForegroundColor White
Write-Host "   Instagram: Stories, bio link, posts with hashtags" -ForegroundColor White
Write-Host "   TikTok: Create video reviews, "link in bio"" -ForegroundColor White
Write-Host "   YouTube: Review videos, description links" -ForegroundColor White
Write-Host "   Quora: Answer questions with helpful links" -ForegroundColor White
Write-Host "   Medium: Write articles recommending products" -ForegroundColor White

# Action items
Write-Host "`n🎯 ACTIONS FOR TODAY:" -ForegroundColor Magenta
Write-Host "   ☐ 1. Join 3 affiliate programs (Amazon, ClickBank, ShareASale)" -ForegroundColor White
Write-Host "   ☐ 2. Create accounts on all social platforms" -ForegroundColor White
Write-Host "   ☐ 3. Post 5 affiliate links on Reddit TODAY" -ForegroundColor White
Write-Host "   ☐ 4. Write 1 Medium article with affiliate links" -ForegroundColor White
Write-Host "   ☐ 5. Tweet 3 times about each product" -ForegroundColor White
Write-Host "   ☐ 6. Join 10 Facebook groups in your niche" -ForegroundColor White
Write-Host "   ☐ 7. Answer 5 questions on Quora with helpful info + links" -ForegroundColor White

Write-Host "`n💰 INCOME POTENTIAL:" -ForegroundColor Yellow
Write-Host "   10 sales/day × $50 avg commission = $500/day = $15,000/month!" -ForegroundColor Green
Write-Host "   Scale to 100 sales/day = $150,000/month!" -ForegroundColor Green

# Save to file
$output = @"
AFFILIATE MARKETING BLAST - $timestamp
========================================

TOP PRODUCTS TO PROMOTE:
$(foreach($p in $PRODUCTS) { "$($p.Name) - $($p.Commission): $($p.URL)`n" })

SAMPLE POSTS READY TO USE
========================================

"@
$output | Out-File -FilePath "$env:USERPROFILE\.openclaw\workspace\data\affiliate_posts.txt"

Add-Content -Path $LOG_FILE -Value "[$timestamp] Affiliate blast generated"

Write-Host "`n✅ Affiliate marketing pack saved to data folder!" -ForegroundColor Green
Write-Host "🔥 Start promoting NOW!" -ForegroundColor Cyan
