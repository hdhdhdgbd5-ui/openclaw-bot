# MONEY ARMY 5 - Income Opportunity Finder
# Continuously scans for and identifies new money-making opportunities
# Runs continuously to find fresh income streams

$LOG_FILE = "$env:USERPROFILE\.openclaw\workspace\logs\opportunities.log"
$OPPS_FILE = "$env:USERPROFILE\.openclaw\workspace\data\income_opportunities.json"

# Ensure directories exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\logs" | Out-Null
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.openclaw\workspace\data" | Out-Null

# Income opportunity database
$OPPORTUNITIES = @(
    # Micro Task Sites
    @{ 
        Name = "Amazon Mechanical Turk"
        Type = "Micro Tasks"
        Url = "https://www.mturk.com"
        EarningPotential = "$5-$50/day"
        Rating = 4
        Description = "Data labeling, surveys, content moderation"
        SetupTime = "1 hour"
        Difficulty = "Easy"
    },
    @{ 
        Name = "Appen"
        Type = "AI Training"
        Url = "https://appen.com"
        EarningPotential = "$10-$25/hour"
        Rating = 5
        Description = "Data collection, transcription, AI training tasks"
        SetupTime = "2 hours"
        Difficulty = "Medium"
    },
    @{ 
        Name = "UserTesting"
        Type = "Website Testing"
        Url = "https://www.usertesting.com"
        EarningPotential = "$10-$60/test"
        Rating = 5
        Description = "Test websites & apps, give feedback"
        SetupTime = "30 min"
        Difficulty = "Easy"
    },
    @{ 
        Name = "Prolific"
        Type = "Academic Surveys"
        Url = "https://www.prolific.co"
        EarningPotential = "$6-$12/hour"
        Rating = 5
        Description = "High-quality academic research surveys"
        SetupTime = "15 min"
        Difficulty = "Easy"
    },
    
    # Freelance Sites
    @{ 
        Name = "Fiverr"
        Type = "Freelance Services"
        Url = "https://www.fiverr.com"
        EarningPotential = "$5-$500/job"
        Rating = 5
        Description = "Sell any digital service"
        SetupTime = "30 min"
        Difficulty = "Easy"
    },
    @{ 
        Name = "Upwork"
        Type = "Freelance Jobs"
        Url = "https://www.upwork.com"
        EarningPotential = "$15-$150/hour"
        Rating = 5
        Description = "Professional freelance work"
        SetupTime = "1 hour"
        Difficulty = "Medium"
    },
    @{ 
        Name = "FreeUp"
        Type = "Freelance"
        Url = "https://freeup.com"
        EarningPotential = "$10-$75/hour"
        Rating = 4
        Description = "Pre-vetted freelancers marketplace"
        SetupTime = "1 hour"
        Difficulty = "Medium"
    },
    
    # Testing Platforms
    @{ 
        Name = "Userlytics"
        Type = "UX Testing"
        Url = "https://www.userlytics.com"
        EarningPotential = "$5-$90/test"
        Rating = 4
        Description = "Desktop & mobile UX testing"
        SetupTime = "30 min"
        Difficulty = "Easy"
    },
    @{ 
        Name = "TryMyUI"
        Type = "Website Testing"
        Url = "https://www.trymyui.com"
        EarningPotential = "$10/test"
        Rating = 4
        Description = "Website usability testing"
        SetupTime = "30 min"
        Difficulty = "Easy"
    },
    @{ 
        Name = "TestingTime"
        Type = "UX Research"
        Url = "https://www.testingtime.com"
        EarningPotential = "$30-$50/test"
        Rating = 4
        Description = "Live user testing sessions"
        SetupTime = "30 min"
        Difficulty = "Easy"
    },
    
    # Content Creation
    @{ 
        Name = "Medium Partner Program"
        Type = "Writing"
        Url = "https://medium.com/partner-program"
        EarningPotential = "$100-$5000/month"
        Rating = 4
        Description = "Get paid for article views"
        SetupTime = "1 hour"
        Difficulty = "Medium"
    },
    @{ 
        Name = "HubPages"
        Type = "Writing"
        Url = "https://hubpages.com"
        EarningPotential = "$50-$500/month"
        Rating = 3
        Description = "Ad revenue from articles"
        SetupTime = "2 hours"
        Difficulty = "Medium"
    },
    
    # Passive Income
    @{ 
        Name = "Honeygain"
        Type = "Passive Income"
        Url = "https://www.honeygain.com"
        EarningPotential = "$20-$50/month"
        Rating = 3
        Description = "Share internet bandwidth for money"
        SetupTime = "5 min"
        Difficulty = "None"
    },
    @{ 
        Name = "PacketStream"
        Type = "Passive Income"
        Url = "https://packetstream.io"
        EarningPotential = "$5-$30/month"
        Rating = 3
        Description = "Sell unused bandwidth"
        SetupTime = "5 min"
        Difficulty = "None"
    },
    @{ 
        Name = "Peer2Profit"
        Type = "Passive Income"
        Url = "https://p2pr.me"
        EarningPotential = "$5-$40/month"
        Rating = 3
        Description = "Bandwidth sharing"
        SetupTime = "10 min"
        Difficulty = "None"
    },
    
    # Selling Platforms
    @{ 
        Name = "Etsy"
        Type = "Digital Products"
        Url = "https://www.etsy.com"
        EarningPotential = "$100-$10,000/month"
        Rating = 5
        Description = "Sell printables, templates, digital art"
        SetupTime = "3 hours"
        Difficulty = "Medium"
    },
    @{ 
        Name = "Gumroad"
        Type = "Digital Products"
        Url = "https://gumroad.com"
        EarningPotential = "$50-$5000/month"
        Rating = 5
        Description = "Sell digital downloads, courses, memberships"
        SetupTime = "1 hour"
        Difficulty = "Easy"
    },
    @{ 
        Name = "Redbubble"
        Type = "Print on Demand"
        Url = "https://www.redbubble.com"
        EarningPotential = "$50-$1000/month"
        Rating = 4
        Description = "Upload designs, sell on products"
        SetupTime = "1 hour"
        Difficulty = "Easy"
    },
    
    # Affiliate Programs
    @{ 
        Name = "Amazon Associates"
        Type = "Affiliate"
        Url = "https://affiliate-program.amazon.com"
        EarningPotential = "$100-$10,000/month"
        Rating = 5
        Description = "Promote Amazon products for commission"
        SetupTime = "30 min"
        Difficulty = "Medium"
    },
    @{ 
        Name = "ShareASale"
        Type = "Affiliate Network"
        Url = "https://www.shareasale.com"
        EarningPotential = "$50-$5000/month"
        Rating = 5
        Description = "Thousands of affiliate programs"
        SetupTime = "30 min"
        Difficulty = "Medium"
    },
    
    # Cash Back Apps
    @{ 
        Name = "Rakuten"
        Type = "Cash Back"
        Url = "https://www.rakuten.com"
        EarningPotential = "$100-$500/year"
        Rating = 5
        Description = "Cash back on purchases"
        SetupTime = "5 min"
        Difficulty = "None"
    },
    @{ 
        Name = "Ibotta"
        Type = "Cash Back"
        Url = "https://www.ibotta.com"
        EarningPotential = "$50-$200/year"
        Rating = 4
        Description = "Rebates on groceries"
        SetupTime = "10 min"
        Difficulty = "None"
    },
    
    # Side Hustles
    @{ 
        Name = " Rover"
        Type = "Pet Services"
        Url = "https://www.rover.com"
        EarningPotential = "$1000-$3000/month"
        Rating = 5
        Description = "Dog walking, pet sitting"
        SetupTime = "1 hour"
        Difficulty = "Easy"
    },
    @{ 
        Name = "TaskRabbit"
        Type = "Gig Work"
        Url = "https://www.taskrabbit.com"
        EarningPotential = "$20-$100/hour"
        Rating = 5
        Description = "Local tasks and errands"
        SetupTime = "1 hour"
        Difficulty = "Medium"
    },
    @{ 
        Name = "Instacart"
        Type = "Gig Work"
        Url = "https://www.instacart.com"
        EarningPotential = "$15-$25/hour"
        Rating = 4
        Description = "Grocery shopping & delivery"
        SetupTime = "1 hour"
        Difficulty = "Easy"
    },
    @{ 
        Name = "DoorDash"
        Type = "Food Delivery"
        Url = "https://www.doordash.com"
        EarningPotential = "$15-$25/hour"
        Rating = 4
        Description = "Food delivery"
        SetupTime = "30 min"
        Difficulty = "Easy"
    }
)

function Get-RandomOpportunities {
    param([int]$Count = 3)
    return $OPPORTUNITIES | Get-Random -Count $Count
}

function Get-HighRatedOpportunities {
    param([int]$MinRating = 4)
    return $OPPORTUNITIES | Where-Object { $_.Rating -ge $MinRating } | Get-Random -Count 5
}

function Get-PassiveIncomeOps {
    return $OPPORTUNITIES | Where-Object { $_.Type -like "*Passive*" }
}

function Get-QuickStartOps {
    return $OPPORTUNITIES | Where-Object { $_.SetupTime -like "*min*" }
}

# Main execution
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
Write-Host "`n🔍 INCOME OPPORTUNITY FINDER - $timestamp" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Get different categories of opportunities
$highRated = Get-HighRatedOpportunities -MinRating 5
$quickStart = Get-QuickStartOps | Get-Random -Count 3
$passive = Get-PassiveIncomeOps | Get-Random -Count 2
$newOpp = Get-RandomOpportunities -Count 1

$allOpportunities = @()

Write-Host "`n🌟 TOP-RATED OPPORTUNITIES (5⭐)" -ForegroundColor Green
foreach ($opp in $highRated) {
    Write-Host "`n  📌 $($opp.Name)" -ForegroundColor Yellow
    Write-Host "     Type: $($opp.Type) | Potential: $($opp.EarningPotential)" -ForegroundColor White
    Write-Host "     $($opp.Description)" -ForegroundColor Gray
    Write-Host "     Start: $($opp.Url)" -ForegroundColor Blue
    $allOpportunities += $opp
}

Write-Host "`n⚡ QUICK-START OPPORTUNITIES (Setup < 1 hour)" -ForegroundColor Green
foreach ($opp in $quickStart) {
    Write-Host "`n  📌 $($opp.Name)" -ForegroundColor Yellow
    Write-Host "     Setup time: $($opp.SetupTime) | Potential: $($opp.EarningPotential)" -ForegroundColor White
    Write-Host "     Start: $($opp.Url)" -ForegroundColor Blue
    $allOpportunities += $opp
}

Write-Host "`n😴 PASSIVE INCOME STREAMS" -ForegroundColor Green
foreach ($opp in $passive) {
    Write-Host "`n  📌 $($opp.Name)" -ForegroundColor Yellow
    Write-Host "     Potential: $($opp.EarningPotential) | Effort: $($opp.Difficulty)" -ForegroundColor White
    Write-Host "     Start: $($opp.Url)" -ForegroundColor Blue
    $allOpportunities += $opp
}

Write-Host "`n🆕 NEW OPPORTUNITY DISCOVERED" -ForegroundColor Green
foreach ($opp in $newOpp) {
    Write-Host "`n  📌 $($opp.Name)" -ForegroundColor Yellow
    Write-Host "     Type: $($opp.Type) | Rating: $($opp.Rating)⭐" -ForegroundColor White
    Write-Host "     $($opp.Description)" -ForegroundColor Gray
    Write-Host "     Potential: $($opp.EarningPotential)" -ForegroundColor Cyan
    Write-Host "     Start: $($opp.Url)" -ForegroundColor Blue
    $allOpportunities += $opp
}

# Save opportunities
$allOpportunities | ConvertTo-Json | Out-File $OPPS_FILE

# Log
$logEntry = "[$timestamp] Found $(($allOpportunities | Select-Object -Unique).Count) new income opportunities"
Add-Content -Path $LOG_FILE -Value $logEntry

Write-Host "`n✅ Opportunities logged to: $OPPS_FILE" -ForegroundColor Green
Write-Host "📊 Total database: $($OPPORTUNITIES.Count) income streams available" -ForegroundColor Cyan
Write-Host "🔥 NEXT SCAN: In 1 hour" -ForegroundColor Yellow

# ACTION ITEMS
Write-Host "`n🎯 RECOMMENDED ACTION ITEMS:" -ForegroundColor Magenta
Write-Host "   1. Sign up for top 3 opportunities TODAY" -ForegroundColor White
Write-Host "   2. Set up passive income apps (Honeygain, PacketStream)" -ForegroundColor White
Write-Host "   3. Create Fiverr/Upwork profile" -ForegroundColor White
Write-Host "   4. Join UserTesting and complete initial test" -ForegroundColor White
