#!/usr/bin/env node

/**
 * Custom Deploy - Multi-platform deployment tool
 * Deploy to GitHub Pages, Vercel, Netlify, Cloudflare Pages
 * Uses native APIs (no external CLI dependencies)
 */

function usage() {
  console.error(`Usage: deploy.mjs <platform> <path> [options]
  
Platforms:
  github-pages   Deploy static site to GitHub Pages
  vercel         Deploy to Vercel using API
  netlify        Deploy to Netlify using API
  cloudflare     Deploy to Cloudflare Pages

Options:
  -h, --help                 Show this help
  --repo <owner/repo>        GitHub repository (github-pages)
  --branch <name>            Branch to deploy (default: gh-pages)
  --token <token>            API token (or use env var)
  --project <name>           Project name (vercel/netlify/cloudflare)
  --site-id <id>             Site ID (netlify)
  --account-id <id>          Account ID (cloudflare)
  --domain <domain>          Custom domain
  --prod                     Deploy to production (vercel)
  
Environment Variables:
  GITHUB_TOKEN               GitHub Personal Access Token
  VERCEL_TOKEN               Vercel API Token
  NETLIFY_TOKEN              Netlify API Token
  CLOUDFLARE_API_TOKEN       Cloudflare API Token
  CLOUDFLARE_ACCOUNT_ID      Cloudflare Account ID

Examples:
  # GitHub Pages
  deploy.mjs github-pages ./dist --repo owner/my-app --branch gh-pages
  
  # Vercel
  deploy.mjs vercel ./dist --project my-app --prod
  
  # Netlify
  deploy.mjs netlify ./dist --project my-app
  
  # Cloudflare Pages
  deploy.mjs cloudflare ./dist --project my-app
`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const platform = args[0].toLowerCase();
const deployPath = args[1];

if (!deployPath) {
  console.error("Error: Deploy path is required");
  usage();
}

// Parse options
const options = {};
let i = 2;
while (i < args.length) {
  const arg = args[i];
  if (arg.startsWith("--")) {
    const key = arg.slice(2);
    if (args[i + 1] && !args[i + 1].startsWith("--")) {
      options[key] = args[i + 1];
      i += 2;
    } else if (key === "prod") {
      options.prod = true;
      i++;
    } else {
      options[key] = true;
      i++;
    }
  } else if (arg.startsWith("-")) {
    // Short options
    if (arg === "-h") usage();
    i++;
  } else {
    i++;
  }
}

// Route to appropriate platform handler
switch (platform) {
  case "github-pages":
  case "github":
    await deployGitHubPages(deployPath, options);
    break;
  case "vercel":
    await deployVercel(deployPath, options);
    break;
  case "netlify":
    await deployNetlify(deployPath, options);
    break;
  case "cloudflare":
  case "cloudflare-pages":
    await deployCloudflarePages(deployPath, options);
    break;
  default:
    console.error(`Unknown platform: ${platform}`);
    console.error("Supported: github-pages, vercel, netlify, cloudflare");
    process.exit(1);
}

/**
 * Deploy to GitHub Pages using GitHub API
 */
async function deployGitHubPages(deployPath, options) {
  const repo = options.repo;
  const branch = options.branch || "gh-pages";
  const token = options.token || process.env.GITHUB_TOKEN;
  
  if (!token) {
    console.error("Error: GitHub token required (--token or GITHUB_TOKEN)");
    process.exit(1);
  }
  if (!repo) {
    console.error("Error: GitHub repository required (--repo owner/repo)");
    process.exit(1);
  }
  
  const [owner, repoName] = repo.split("/");
  if (!owner || !repoName) {
    console.error("Error: Invalid repo format. Use owner/repo");
    process.exit(1);
  }
  
  console.log(`Deploying to GitHub Pages: ${repo} (branch: ${branch})`);
  
  // Read files from deploy path
  const fs = await import("fs");
  const path = await import("path");
  
  if (!fs.existsSync(deployPath)) {
    console.error(`Error: Deploy path does not exist: ${deployPath}`);
    process.exit(1);
  }
  
  const files = {};
  
  function walkDir(dir, basePath = "") {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.join(basePath, entry.name);
      
      if (entry.isDirectory()) {
        walkDir(fullPath, relativePath);
      } else {
        const content = fs.readFileSync(fullPath);
        files[relativePath] = content.toString("base64");
      }
    }
  }
  
  walkDir(deployPath);
  
  if (Object.keys(files).length === 0) {
    console.error("Error: No files found in deploy path");
    process.exit(1);
  }
  
  console.log(`Uploading ${Object.keys(files).length} files...`);
  
  // Get the default branch SHA for the commit
  const repoInfoResp = await fetch(`https://api.github.com/repos/${owner}/${repoName}`, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    }
  });
  
  if (!repoInfoResp.ok) {
    const err = await repoInfoResp.text();
    console.error(`Failed to get repo info: ${err}`);
    process.exit(1);
  }
  
  const repoInfo = await repoInfoResp.json();
  const defaultBranch = repoInfo.default_branch;
  
  // Get the default branch commit SHA
  const branchResp = await fetch(`https://api.github.com/repos/${owner}/${repoName}/branches/${defaultBranch}`, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    }
  });
  
  if (!branchResp.ok) {
    const err = await branchResp.text();
    console.error(`Failed to get branch info: ${err}`);
    process.exit(1);
  }
  
  const branchInfo = await branchResp.json();
  const baseSha = branchInfo.commit.sha;
  
  // Create blob for each file
  const blobs = {};
  for (const [filePath, content] of Object.entries(files)) {
    const blobResp = await fetch(`https://api.github.com/repos/${owner}/${repoName}/git/blobs`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        content: content,
        encoding: "base64"
      })
    });
    
    if (!blobResp.ok) {
      const err = await blobResp.text();
      console.error(`Failed to create blob for ${filePath}: ${err}`);
      process.exit(1);
    }
    
    const blobInfo = await blobResp.json();
    blobs[filePath] = {
      path: filePath,
      mode: "100644",
      type: "blob",
      sha: blobInfo.sha
    };
  }
  
  // Create tree
  const treeResp = await fetch(`https://api.github.com/repos/${owner}/${repoName}/git/trees`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      base_tree: baseSha,
      tree: Object.values(blobs)
    })
  });
  
  if (!treeResp.ok) {
    const err = await treeResp.text();
    console.error(`Failed to create tree: ${err}`);
    process.exit(1);
  }
  
  const treeInfo = await treeResp.json();
  
  // Create commit
  const commitResp = await fetch(`https://api.github.com/repos/${owner}/${repoName}/git/commits`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      message: "Deploy to GitHub Pages",
      tree: treeInfo.sha,
      parents: [baseSha]
    })
  });
  
  if (!commitResp.ok) {
    const err = await commitResp.text();
    console.error(`Failed to create commit: ${err}`);
    process.exit(1);
  }
  
  const commitInfo = await commitResp.json();
  
  // Update reference
  const refResp = await fetch(`https://api.github.com/repos/${owner}/${repoName}/git/refs/heads/${branch}`, {
    method: "PATCH",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      sha: commitInfo.sha,
      force: true
    })
  });
  
  // If branch doesn't exist, create it
  if (!refResp.ok) {
    const createRefResp = await fetch(`https://api.github.com/repos/${owner}/${repoName}/git/refs`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        ref: `refs/heads/${branch}`,
        sha: commitInfo.sha
      })
    });
    
    if (!createRefResp.ok) {
      const err = await createRefResp.text();
      console.error(`Failed to create branch: ${err}`);
      process.exit(1);
    }
  }
  
  // Check if GitHub Pages is enabled, enable if not
  const pagesResp = await fetch(`https://api.github.com/repos/${owner}/${repoName}/pages`, {
    method: "GET",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28"
    }
  });
  
  if (pagesResp.status === 404) {
    // Enable GitHub Pages
    await fetch(`https://api.github.com/repos/${owner}/${repoName}/pages`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        source: {
          branch: branch,
          path: "/"
        }
      })
    });
  }
  
  console.log(`✅ Deployed to GitHub Pages!`);
  console.log(`   URL: https://${owner}.github.io/${repoName}/`);
}

/**
 * Deploy to Vercel using Vercel API
 */
async function deployVercel(deployPath, options) {
  const token = options.token || process.env.VERCEL_TOKEN;
  const projectName = options.project;
  const isProd = options.prod === true;
  
  if (!token) {
    console.error("Error: Vercel token required (--token or VERCEL_TOKEN)");
    process.exit(1);
  }
  if (!projectName) {
    console.error("Error: Project name required (--project <name>)");
    process.exit(1);
  }
  
  console.log(`Deploying to Vercel: ${projectName}${isProd ? " (production)" : " (preview)"}`);
  
  const fs = await import("fs");
  const path = await import("path");
  
  if (!fs.existsSync(deployPath)) {
    console.error(`Error: Deploy path does not exist: ${deployPath}`);
    process.exit(1);
  }
  
  // Create a ZIP file with the deployment files
  const files = [];
  
  function walkDir(dir, basePath = "") {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.join(basePath, entry.name);
      
      if (entry.isDirectory()) {
        walkDir(fullPath, relativePath);
      } else {
        const content = fs.readFileSync(fullPath);
        files.push({
          file: relativePath,
          data: content.toString("base64")
        });
      }
    }
  }
  
  walkDir(deployPath);
  
  if (files.length === 0) {
    console.error("Error: No files found in deploy path");
    process.exit(1);
  }
  
  console.log(`Uploading ${files.length} files...`);
  
  // Create deployment using Vercel API
  // First, create a new deployment
  const manifest = {
    name: projectName,
    files: files,
    version: 5,
    functions: {},
    routes: null,
    env: {},
    build: {}
  };
  
  // Actually, for Vercel we need to use their deployment API
  // Let's use the simpler approach: create a new deployment via files API
  
  // Get project info
  const projectResp = await fetch(`https://api.vercel.com/v6/projects/${projectName}`, {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });
  
  let projectId;
  if (projectResp.ok) {
    const projectData = await projectResp.json();
    projectId = projectData.id;
  } else {
    // Project doesn't exist, create it
    console.log("Creating new Vercel project...");
    const createResp = await fetch("https://api.vercel.com/v6/projects", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: projectName,
        framework: null,
        public: true
      })
    });
    
    if (!createResp.ok) {
      const err = await createResp.text();
      console.error(`Failed to create project: ${err}`);
      process.exit(1);
    }
    
    const createData = await createResp.json();
    projectId = createData.id;
  }
  
  // Create deployment
  const deployResp = await fetch(`https://api.vercel.com/v6/deployments`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: projectName,
      project: projectId,
      files: files,
      version: 5,
      target: isProd ? "production" : "preview"
    })
  });
  
  if (!deployResp.ok) {
    const err = await deployResp.text();
    console.error(`Failed to create deployment: ${err}`);
    process.exit(1);
  }
  
  const deployData = await deployResp.json();
  
  // Wait for deployment ready
  console.log("Building deployment...");
  let ready = false;
  let attempts = 0;
  const maxAttempts = 60;
  
  while (!ready && attempts < maxAttempts) {
    await new Promise(r => setTimeout(r, 2000));
    
    const statusResp = await fetch(`https://api.vercel.com/v6/deployments/${deployData.uid}`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
    
    if (statusResp.ok) {
      const statusData = await statusResp.json();
      console.log(`   Status: ${statusData.state}`);
      
      if (statusData.state === "READY" || statusData.state === "ERROR") {
        ready = true;
        
        if (statusData.state === "READY") {
          console.log(`✅ Deployed to Vercel!`);
          console.log(`   URL: https://${statusData.url}`);
        } else {
          console.error(`Deployment failed: ${statusData.errorMessage}`);
          process.exit(1);
        }
      }
    }
    
    attempts++;
  }
  
  if (!ready) {
    console.log("⏳ Deployment still building...");
    console.log(`   Check: https://vercel.com/dashboard`);
  }
}

/**
 * Deploy to Netlify using Netlify API
 */
async function deployNetlify(deployPath, options) {
  const token = options.token || process.env.NETLIFY_TOKEN;
  const siteId = options.siteId || options.project;
  
  if (!token) {
    console.error("Error: Netlify token required (--token or NETLIFY_TOKEN)");
    process.exit(1);
  }
  
  console.log(`Deploying to Netlify...`);
  
  const fs = await import("fs");
  const path = await import("path");
  
  if (!fs.existsSync(deployPath)) {
    console.error(`Error: Deploy path does not exist: ${deployPath}`);
    process.exit(1);
  }
  
  // Get or create site
  let currentSiteId = siteId;
  
  if (!currentSiteId) {
    // List sites to find existing
    const sitesResp = await fetch("https://api.netlify.com/api/v1/sites", {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });
    
    if (sitesResp.ok) {
      const sites = await sitesResp.json();
      if (sites.length > 0) {
        currentSiteId = sites[0].id;
        console.log(`Using existing site: ${sites[0].url}`);
      }
    }
  }
  
  // Upload files via deploy hook or API
  // For simplicity, create a deploy.zip and upload
  const files = [];
  
  function walkDir(dir, basePath = "") {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.join(basePath, entry.name).replace(/\\/g, "/");
      
      if (entry.isDirectory()) {
        walkDir(fullPath, relativePath);
      } else {
        const content = fs.readFileSync(fullPath);
        files.push({
          path: relativePath,
          content: content.toString("base64")
        });
      }
    }
  }
  
  walkDir(deployPath);
  
  if (files.length === 0) {
    console.error("Error: No files found in deploy path");
    process.exit(1);
  }
  
  console.log(`Uploading ${files.length} files...`);
  
  // For Netlify, we need to create a site or use deploy API
  // Using the direct deploy API
  const deployData = {
    files: files,
    async: true
  };
  
  let deployUrl = "https://api.netlify.com/api/v1/sites";
  if (currentSiteId) {
    deployUrl = `https://api.netlify.com/api/v1/sites/${currentSiteId}/deploys`;
  }
  
  const deployResp = await fetch(deployUrl, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(deployData)
  });
  
  if (!deployResp.ok) {
    const err = await deployResp.text();
    console.error(`Failed to create deploy: ${err}`);
    process.exit(1);
  }
  
  const result = await deployResp.json();
  
  if (result.deploy_id) {
    console.log("✅ Deploy initiated to Netlify!");
    console.log(`   Deploy ID: ${result.deploy_id}`);
    console.log(`   Check: https://app.netlify.com/sites`);
  } else if (result.id) {
    console.log("✅ Deployed to Netlify!");
    console.log(`   URL: ${result.url}`);
  } else {
    console.log("✅ Deploy initiated!");
    console.log(`   Check: https://app.netlify.com/sites`);
  }
}

/**
 * Deploy to Cloudflare Pages using Cloudflare API
 */
async function deployCloudflarePages(deployPath, options) {
  const token = options.token || process.env.CLOUDFLARE_API_TOKEN;
  const accountId = options.accountId || process.env.CLOUDFLARE_ACCOUNT_ID;
  const projectName = options.project;
  
  if (!token) {
    console.error("Error: Cloudflare token required (--token or CLOUDFLARE_API_TOKEN)");
    process.exit(1);
  }
  if (!accountId) {
    console.error("Error: Cloudflare account ID required (--account-id or CLOUDFLARE_ACCOUNT_ID)");
    process.exit(1);
  }
  if (!projectName) {
    console.error("Error: Project name required (--project <name>)");
    process.exit(1);
  }
  
  console.log(`Deploying to Cloudflare Pages: ${projectName}`);
  
  const fs = await import("fs");
  const path = await import("path");
  
  if (!fs.existsSync(deployPath)) {
    console.error(`Error: Deploy path does not exist: ${deployPath}`);
    process.exit(1);
  }
  
  // Get or create project
  let projectId = null;
  
  const projectsResp = await fetch(`https://api.cloudflare.com/client/v4/accounts/${accountId}/pages/projects`, {
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    }
  });
  
  if (projectsResp.ok) {
    const projectsData = await projectsResp.json();
    const existing = projectsData.result.find(p => p.name === projectName);
    if (existing) {
      projectId = existing.name;
      console.log(`Using existing project: ${projectName}`);
    }
  }
  
  if (!projectId) {
    // Create project
    console.log(`Creating new Cloudflare Pages project...`);
    const createResp = await fetch(`https://api.cloudflare.com/client/v4/accounts/${accountId}/pages/projects`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: projectName,
        production_branch: "main",
        src_config: {
          type: "direct_upload"
        }
      })
    });
    
    if (!createResp.ok) {
      const err = await createResp.text();
      console.error(`Failed to create project: ${err}`);
      process.exit(1);
    }
    
    const createData = await createResp.json();
    projectId = createData.result.name;
  }
  
  // Create deployment
  // First, get upload URL
  const uploadResp = await fetch(`https://api.cloudflare.com/client/v4/accounts/${accountId}/pages/projects/${projectName}/deployments`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      branch: "main",
      skip_processing: false,
      auto_modify_webhook_configurations: false
    })
  });
  
  if (!uploadResp.ok) {
    const err = await uploadResp.text();
    console.error(`Failed to initiate deployment: ${err}`);
    process.exit(1);
  }
  
  const uploadData = await uploadResp.json();
  const uploadUrl = uploadData.result.upload_url;
  
  // Prepare files for upload
  const files = [];
  
  function walkDir(dir, basePath = "") {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      const relativePath = path.join(basePath, entry.name).replace(/\\/g, "/");
      
      if (entry.isDirectory()) {
        walkDir(fullPath, relativePath);
      } else {
        const content = fs.readFileSync(fullPath);
        files.push({
          key: relativePath,
          value: content.toString("base64"),
          metadata: {
            contentType: getContentType(relativePath)
          }
        });
      }
    }
  }
  
  walkDir(deployPath);
  
  if (files.length === 0) {
    console.error("Error: No files found in deploy path");
    process.exit(1);
  }
  
  console.log(`Uploading ${files.length} files...`);
  
  // Upload files
  const formData = new FormData();
  for (const file of files) {
    // Convert base64 to Uint8Array
    const binary = atob(file.value);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      bytes[i] = binary.charCodeAt(i);
    }
    
    formData.append("files", new Blob([bytes], { type: file.metadata.contentType }), file.key);
  }
  
  const uploadFilesResp = await fetch(uploadUrl, {
    method: "POST",
    body: formData
  });
  
  if (!uploadFilesResp.ok) {
    const err = await uploadFilesResp.text();
    console.error(`Failed to upload files: ${err}`);
    process.exit(1);
  }
  
  console.log("✅ Deployed to Cloudflare Pages!");
  console.log(`   Project: ${projectName}`);
  console.log(`   Check: https://dash.cloudflare.com/${accountId}/pages`);
}

function getContentType(filename) {
  const ext = filename.split(".").pop().toLowerCase();
  const types = {
    "html": "text/html",
    "htm": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "json": "application/json",
    "txt": "text/plain",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "svg": "image/svg+xml",
    "ico": "image/x-icon",
    "woff": "font/woff",
    "woff2": "font/woff2",
    "ttf": "font/ttf",
    "eot": "application/vnd.ms-fontobject"
  };
  return types[ext] || "application/octet-stream";
}
