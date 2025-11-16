/**
 * Project Switcher JavaScript
 * مدیریت تغییر پروژه کاربر
 */

// تابع باز/بسته کردن dropdown
function toggleProjectDropdown() {
    const dropdown = document.getElementById('projectDropdown');
    const switcher = document.getElementById('projectSwitcher');
    
    if (dropdown && switcher) {
        if (dropdown.style.display === 'none' || !dropdown.style.display) {
            dropdown.style.display = 'flex';
            switcher.classList.add('open');
        } else {
            dropdown.style.display = 'none';
            switcher.classList.remove('open');
        }
    }
}

// بستن dropdown با کلیک بیرون
document.addEventListener('click', function(e) {
    const switcher = document.getElementById('projectSwitcher');
    const dropdown = document.getElementById('projectDropdown');
    
    if (switcher && dropdown && !switcher.contains(e.target)) {
        dropdown.style.display = 'none';
        switcher.classList.remove('open');
    }
});

// تابع تغییر پروژه
async function switchProject(projectId) {
    const dropdown = document.getElementById('projectDropdown');
    
    if (!dropdown) {
        console.error('Project dropdown not found');
        return;
    }
    
    // نمایش loading
    dropdown.style.opacity = '0.5';
    dropdown.style.pointerEvents = 'none';
    
    try {
        const response = await fetch('/api/v1/Project/switch/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ project_id: projectId })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // Reload صفحه برای نمایش داده‌های پروژه جدید
            location.reload();
        } else {
            alert('خطا در تغییر پروژه: ' + (data.error || 'خطای ناشناخته'));
            dropdown.style.opacity = '1';
            dropdown.style.pointerEvents = 'auto';
        }
    } catch (error) {
        console.error('Error switching project:', error);
        alert('خطا در ارتباط با سرور');
        dropdown.style.opacity = '1';
        dropdown.style.pointerEvents = 'auto';
    }
}

// تابع دریافت CSRF token از cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// بستن dropdown با کلید ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        const dropdown = document.getElementById('projectDropdown');
        const switcher = document.getElementById('projectSwitcher');
        if (dropdown && dropdown.style.display !== 'none') {
            dropdown.style.display = 'none';
            if (switcher) {
                switcher.classList.remove('open');
            }
        }
    }
});

// بارگذاری اطلاعات پروژه‌ها از API
let currentProjectData = null;
let allProjectsData = [];

async function loadProjectData() {
    try {
        // دریافت پروژه‌های کاربر (اول این را می‌گیریم تا allProjectsData کامل باشد)
        const projectsResponse = await fetch('/api/v1/Project/');
        if (projectsResponse.ok) {
            const projects = await projectsResponse.json();
            allProjectsData = projects;
        }
        
        // دریافت پروژه جاری از API
        let currentProjectFromAPI = null;
        try {
            const currentResponse = await fetch('/api/v1/Project/current/');
            if (currentResponse.ok) {
                currentProjectFromAPI = await currentResponse.json();
                // ذخیره در localStorage برای استفاده بعدی
                if (currentProjectFromAPI && currentProjectFromAPI.id) {
                    setCurrentProjectId(currentProjectFromAPI.id);
                }
            }
        } catch (err) {
            console.warn('Could not fetch current project from API:', err);
        }
        
        // اگر پروژه جاری از API گرفته شد، از allProjectsData کامل‌ش کن (برای اطمینان از وجود color و icon)
        if (currentProjectFromAPI && currentProjectFromAPI.id) {
            const fullProjectData = allProjectsData.find(p => p.id === currentProjectFromAPI.id);
            if (fullProjectData) {
                // استفاده از داده‌های کامل از allProjectsData (که شامل color و icon است)
                currentProjectData = fullProjectData;
            } else {
                // اگر در allProjectsData پیدا نشد، از داده API استفاده کن
                currentProjectData = currentProjectFromAPI;
            }
        } else {
            // اگر API کار نکرد، از localStorage استفاده می‌کنیم
            const storedId = getCurrentProjectId();
            if (storedId) {
                currentProjectData = allProjectsData.find(p => p.id === storedId) || null;
            } else if (allProjectsData.length > 0) {
                // اگر هیچ پروژه جاری نبود، از اولین پروژه استفاده کن
                currentProjectData = allProjectsData[0];
            }
        }
        
        // رندر کردن component
        renderProjectSwitcher();
    } catch (error) {
        console.error('Error loading project data:', error);
        // در صورت خطا، component پیش‌فرض را نمایش می‌دهیم
        renderProjectSwitcher();
    }
}

// رندر کردن project switcher component
function renderProjectSwitcher() {
    const switcherContainer = document.getElementById('projectSwitcherContainer');
    if (!switcherContainer) return;
    
    // اگر currentProjectData هنوز تنظیم نشده، از allProjectsData پیدا کن
    if (!currentProjectData) {
        const currentProjectId = getCurrentProjectId();
        currentProjectData = allProjectsData.find(p => p.id === currentProjectId) || allProjectsData[0] || null;
    }
    
    // اطمینان از وجود color و icon در currentProjectData
    if (currentProjectData && currentProjectData.id) {
        const fullProjectData = allProjectsData.find(p => p.id === currentProjectData.id);
        if (fullProjectData) {
            // استفاده از داده‌های کامل از allProjectsData (که شامل color و icon است)
            currentProjectData = fullProjectData;
        }
    }
    
    // ساخت HTML component
    let html = '<div class="project-switcher" id="projectSwitcher">';
    html += '<div class="current-project-display" onclick="toggleProjectDropdown()">';
    
    if (currentProjectData) {
        // استفاده از color و icon از currentProjectData (که حالا شامل این فیلدهاست)
        const icon = (currentProjectData.icon && currentProjectData.icon.trim()) || 'fa-building';
        const color = (currentProjectData.color && currentProjectData.color.trim()) || '#667eea';
        html += `<i class="fas ${icon}" style="color: ${color}; font-size: 18px;"></i>`;
        html += `<span class="project-name">${currentProjectData.name || 'بدون نام'}</span>`;
    } else {
        html += '<i class="fas fa-building" style="color: #667eea; font-size: 18px;"></i>';
        html += '<span class="project-name">هیچ پروژه‌ای انتخاب نشده</span>';
    }
    
    html += '<i class="fas fa-chevron-down dropdown-arrow"></i>';
    html += '</div>';
    
    // Dropdown
    html += '<div class="project-dropdown" id="projectDropdown" style="display: none;">';
    html += '<div class="project-dropdown-header"><span>انتخاب پروژه</span></div>';
    html += '<div class="project-list">';
    
    if (allProjectsData.length > 0) {
        allProjectsData.forEach(project => {
            const isActive = currentProjectData && project.id === currentProjectData.id;
            // استفاده از color و icon از project (که حالا شامل این فیلدهاست)
            const icon = (project.icon && project.icon.trim()) || 'fa-building';
            const color = (project.color && project.color.trim()) || '#667eea';
            
            html += `<div class="project-item ${isActive ? 'active' : ''}" onclick="switchProject(${project.id})" data-project-id="${project.id}">`;
            html += `<i class="fas ${icon}" style="color: ${color};"></i>`;
            html += `<span class="project-item-name">${project.name || 'بدون نام'}</span>`;
            if (project.is_active) {
                html += '<span class="badge badge-success">فعال</span>';
            }
            if (isActive) {
                html += '<i class="fas fa-check project-check-icon"></i>';
            }
            html += '</div>';
        });
    } else {
        html += '<div class="project-item-empty"><span>هیچ پروژه‌ای یافت نشد</span></div>';
    }
    
    html += '</div>';
    html += '</div>';
    html += '</div>';
    
    switcherContainer.innerHTML = html;
    
    // بستن dropdown
    const dropdown = document.getElementById('projectDropdown');
    if (dropdown) {
        dropdown.style.display = 'none';
    }
    
    // رندر کردن badge پروژه جاری در header
    renderProjectBadge();
    
    // نمایش/مخفی کردن هشدار پروژه
    updateProjectWarning();
}

// رندر کردن badge پروژه جاری
function renderProjectBadge() {
    const badgeContainer = document.getElementById('currentProjectBadge');
    if (!badgeContainer) return;
    
    if (currentProjectData) {
        // استفاده از color و icon از currentProjectData (که حالا شامل این فیلدهاست)
        const icon = (currentProjectData.icon && currentProjectData.icon.trim()) || 'fa-building';
        const color = (currentProjectData.color && currentProjectData.color.trim()) || '#fff';
        badgeContainer.innerHTML = `<i class="fas ${icon}" style="color: ${color};"></i> ${currentProjectData.name || 'بدون نام'}`;
        badgeContainer.style.display = 'inline-flex';
    } else {
        badgeContainer.style.display = 'none';
    }
    
    // رندر کردن Project Info Alert برای user_dashboard
    renderProjectInfoAlert();
}

// رندر کردن Project Info Alert (برای user_dashboard)
function renderProjectInfoAlert() {
    const infoContainer = document.getElementById('currentProjectInfo');
    if (!infoContainer) return;
    
    if (currentProjectData) {
        // استفاده از color و icon از currentProjectData (که حالا شامل این فیلدهاست)
        const icon = (currentProjectData.icon && currentProjectData.icon.trim()) || 'fa-building';
        const color = (currentProjectData.color && currentProjectData.color.trim()) || '#667eea';
        const iconElement = document.getElementById('currentProjectIcon');
        const nameElement = document.getElementById('currentProjectName');
        
        if (iconElement) {
            iconElement.className = `fas ${icon}`;
            iconElement.style.color = color;
        }
        if (nameElement) {
            nameElement.textContent = currentProjectData.name || 'بدون نام';
        }
        infoContainer.style.display = 'block';
    } else {
        infoContainer.style.display = 'none';
    }
}

// به‌روزرسانی هشدار پروژه
function updateProjectWarning() {
    const warningDiv = document.getElementById('noProjectWarning');
    if (warningDiv) {
        if (currentProjectData) {
            warningDiv.style.display = 'none';
        } else {
            warningDiv.style.display = 'block';
        }
    }
}

// دریافت ID پروژه جاری
function getCurrentProjectId() {
    // اول از localStorage چک می‌کنیم
    const stored = localStorage.getItem('current_project_id');
    if (stored) {
        return parseInt(stored);
    }
    
    // اگر نبود، از اولین پروژه استفاده می‌کنیم
    if (allProjectsData.length > 0) {
        return allProjectsData[0].id;
    }
    
    return null;
}

// ذخیره پروژه جاری در localStorage
function setCurrentProjectId(projectId) {
    localStorage.setItem('current_project_id', projectId.toString());
}

// به‌روزرسانی تابع switchProject برای ذخیره در localStorage
async function switchProject(projectId) {
    const dropdown = document.getElementById('projectDropdown');
    
    if (!dropdown) {
        console.error('Project dropdown not found');
        return;
    }
    
    // نمایش loading
    dropdown.style.opacity = '0.5';
    dropdown.style.pointerEvents = 'none';
    
    try {
        const response = await fetch('/api/v1/Project/switch/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ project_id: projectId })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            // ذخیره در localStorage
            setCurrentProjectId(projectId);
            // Reload صفحه برای نمایش داده‌های پروژه جدید
            location.reload();
        } else {
            alert('خطا در تغییر پروژه: ' + (data.error || 'خطای ناشناخته'));
            dropdown.style.opacity = '1';
            dropdown.style.pointerEvents = 'auto';
        }
    } catch (error) {
        console.error('Error switching project:', error);
        alert('خطا در ارتباط با سرور');
        dropdown.style.opacity = '1';
        dropdown.style.pointerEvents = 'auto';
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // بارگذاری داده‌های پروژه
    loadProjectData();
});

