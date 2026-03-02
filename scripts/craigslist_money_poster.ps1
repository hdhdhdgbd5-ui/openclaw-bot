# MONEY ARMY 5 - Craigslist Money-Making Poster
# Posts services, gigs, and items for sale to generate income
# Runs every hour

$LOG_FILE = "$env:USERPROFILE\.openclaw\workspace\logs\craigslist_posts.log"
$POSTS_DIR = "$env:USERPROFILE\.openclaw\workspace\data\craigslist_posts"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\logs" | Out-Null
New-Item -ItemType Directory -Force -Path $POSTS_DIR | Out-Null

# Array of Craigslist posting templates
$POST_TEMPLATES = @(
    @{
        Category = "services"
        Title = "Affordable Web Design - $150 Professional Websites"
        Body = @"
Professional Web Design Services

I create beautiful, functional websites for small businesses and individuals.

✓ 3-page responsive website
✓ Mobile-optimized design
✓ Fast loading speed
✓ Basic SEO included
✓ Contact form setup
✓ Social media integration
✓ 48-hour delivery

Perfect for:
- Small businesses
- Restaurants & cafes
- Personal portfolios
- Event pages
- Landing pages

Portfolio available - just ask!

Contact via email to get started.
"@
        Price = "150"
        Location = "your city"
    },
    @{
        Category = "services"
        Title = "Computer Repair & IT Support - Same Day Service"
        Body = @"
Experienced IT technician offering computer services:

Services offered:
- Virus & malware removal ($40)
- Computer cleanup & optimization ($30)
- Software installation ($20)
- Data backup & recovery (starting $50)
- Network setup ($60)
- Hardware upgrades ($50 + parts)
- Remote support available

✓ 5+ years experience
✓ Fast turnaround
✓ Affordable rates
✓ Satisfaction guaranteed

Can come to you or remote support available.

Call or text for quick response!
"@
        Price = "30"
        Location = "your city"
    },
    @{
        Category = "gigs"
        Title = "Hiring: Part-time Virtual Assistant - $15/hour"
        Body = @"
Looking for a reliable virtual assistant to help with daily tasks.

Duties:
- Email management
- Data entry
- Appointment scheduling
- Research tasks
- Social media updates
- Document formatting

Requirements:
- Good written English
- Reliable internet connection
- Available 10-20 hours/week
- Detail-oriented

Pay: $15/hour
Schedule: Flexible hours
Start: Immediately

Please send brief intro about yourself and your experience.
"@
        Compensation = "$15-$20/hour"
        Location = "Remote / Telecommute"
    },
    @{
        Category = "for sale"
        Title = "Gaming Computer Setup - RTX Graphics - $650"
        Body = @"
Selling my gaming rig. Excellent condition, never overclocked.

Specs:
- CPU: Intel i5-10400F
- GPU: RTX 3060 12GB
- RAM: 16GB DDR4
- Storage: 512GB NVMe SSD + 1TB HDD
- PSU: 650W 80+ Bronze
- Case: Mid-tower with RGB
- Includes: Fresh Windows 11 install

Price: $650 OBO

Perfect for 1080p/1440p gaming, streaming, or work.

Local pickup only. Cash preferred.
"@
        Price = "650"
        Location = "your city"
    },
    @{
        Category = "gigs"
        Title = "Need someone for market research - $50 for 1 hour"
        Body = @"
Looking for participants for a brief market research study.

Task: Give feedback on a new app/website (approx 30-45 minutes)

Requirements:
- Age 18-65
- Own a smartphone
- Can follow simple instructions
- Give honest feedback

Pay: $50 cash immediately after completion

This is a one-time gig. Multiple participants needed.

Contact me with:
- Your age
- Type of phone you use
- Best time to schedule

Available times: Weekdays 10am-6pm
"@
        Compensation = "$50 cash (30 mins)"
        Location = "your city"
    },
    @{
        Category = "services"
        Title = "Photo Editing & Retouching - $10 per photo"
        Body = @"
Professional photo editing services:

Services:
✓ Portrait retouching
✓ Background removal
✓ Color correction
✓ Object removal
✓ Photo restoration
✓ Social media optimization

Rates:
- Single photo: $10
- 5+ photos: $7 each
- 20+ photos: $5 each

Turnaround: 24-48 hours

Send me your photos and requirements for a quick quote!
"@
        Price = "10"
        Location = "your city"
    }
)

function Save-CraigslistPost {
    param($Post, $Filename)
    
    $filepath = Join-Path $POSTS_DIR $Filename
    
    $content = @"
========================================
CRAIGSLIST POST - $(Get-Date -Format 'yyyy-MM-dd HH:mm')
========================================
CATEGORY: $($Post.Category)
TITLE: $($Post.Title)
$(if ($Post.Price) { "PRICE: $$($Post.Price)" })
$(if ($Post.Compensation) { "COMPENSATION: $$($Post.Compensation)" })
LOCATION: $($Post.Location)

--- POST BODY ---
$($Post.Body)

--- INSTRUCTIONS ---
1. Go to craigslist.org
2. Click Post to Classifieds
3. Select category: $($Post.Category)
4. Fill in the details above
5. Publish
========================================
"@
    
    $content | Out-File -FilePath $filepath
    return $filepath
}

# Main execution
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "`n=== CRAIGSLIST MONEY POSTER - $timestamp ===" -ForegroundColor Cyan

# Pick random post template
$post = $POST_TEMPLATES | Get-Random
$filename = "craigslist_$(Get-Date -Format 'yyyyMMdd_HHmm').txt"

$filepath = Save-CraigslistPost -Post $post -Filename $filename

# Log the action
$logEntry = "[$timestamp] Generated Craigslist post: $($post.Title) [Category: $($post.Category)]"
Add-Content -Path $LOG_FILE -Value $logEntry
Write-Host $logEntry -ForegroundColor Green
Write-Host "📁 Saved to: $filepath" -ForegroundColor Yellow
Write-Host "🔥 NEXT RUN: In 1 hour" -ForegroundColor Cyan

# Write summary to console
Write-Host "`n--- POST PREVIEW ---" -ForegroundColor Magenta
Write-Host "Title: $($post.Title)" -ForegroundColor White
Write-Host "Category: $($post.Category)" -ForegroundColor White
if ($post.Price) { Write-Host "Price: $$($post.Price)" -ForegroundColor White }
if ($post.Compensation) { Write-Host "Compensation: $$($post.Compensation)" -ForegroundColor Green }
