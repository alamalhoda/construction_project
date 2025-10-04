/**
 * سرویس محاسبات مالی - استفاده از API های سمت سرور
 * این فایل جایگزین محاسبات JavaScript می‌شود
 */

class FinancialCalculationService {
    constructor() {
        this.API_BASE = '/api/v1/';
        this.cache = new Map();
        this.cacheTimeout = 30000; // 30 ثانیه
    }

    /**
     * دریافت تحلیل جامع پروژه
     */
    async getComprehensiveAnalysis(projectId = null) {
        const cacheKey = `comprehensive_analysis_${projectId || 'active'}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const url = `${this.API_BASE}Project/comprehensive_analysis/`;
            const params = new URLSearchParams();
            if (projectId) params.append('project_id', projectId);
            
            const response = await fetch(`${url}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('خطا در دریافت تحلیل جامع:', error);
            throw error;
        }
    }

    /**
     * دریافت متریک‌های سود
     */
    async getProfitMetrics(projectId = null) {
        const cacheKey = `profit_metrics_${projectId || 'active'}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const url = `${this.API_BASE}Project/profit_metrics/`;
            const params = new URLSearchParams();
            if (projectId) params.append('project_id', projectId);
            
            const response = await fetch(`${url}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('خطا در دریافت متریک‌های سود:', error);
            throw error;
        }
    }

    /**
     * دریافت متریک‌های هزینه
     */
    async getCostMetrics(projectId = null) {
        const cacheKey = `cost_metrics_${projectId || 'active'}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const url = `${this.API_BASE}Project/cost_metrics/`;
            const params = new URLSearchParams();
            if (projectId) params.append('project_id', projectId);
            
            const response = await fetch(`${url}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('خطا در دریافت متریک‌های هزینه:', error);
            throw error;
        }
    }

    /**
     * دریافت آمار تفصیلی پروژه
     */
    async getProjectStatistics(projectId = null) {
        const cacheKey = `project_statistics_${projectId || 'active'}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const url = `${this.API_BASE}Project/project_statistics_detailed/`;
            const params = new URLSearchParams();
            if (projectId) params.append('project_id', projectId);
            
            const response = await fetch(`${url}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('خطا در دریافت آمار پروژه:', error);
            throw error;
        }
    }

    /**
     * دریافت آمار تفصیلی سرمایه‌گذار
     */
    async getInvestorStatistics(investorId, projectId = null) {
        const cacheKey = `investor_statistics_${investorId}_${projectId || 'active'}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const url = `${this.API_BASE}Investor/${investorId}/detailed_statistics/`;
            const params = new URLSearchParams();
            if (projectId) params.append('project_id', projectId);
            
            const response = await fetch(`${url}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('خطا در دریافت آمار سرمایه‌گذار:', error);
            throw error;
        }
    }

    /**
     * دریافت نسبت‌های سرمایه‌گذار
     */
    async getInvestorRatios(investorId, projectId = null) {
        const cacheKey = `investor_ratios_${investorId}_${projectId || 'active'}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const url = `${this.API_BASE}Investor/${investorId}/ratios/`;
            const params = new URLSearchParams();
            if (projectId) params.append('project_id', projectId);
            
            const response = await fetch(`${url}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('خطا در دریافت نسبت‌های سرمایه‌گذار:', error);
            throw error;
        }
    }

    /**
     * دریافت خلاصه تمام سرمایه‌گذاران
     */
    async getAllInvestorsSummary(projectId = null) {
        const cacheKey = `all_investors_summary_${projectId || 'active'}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const url = `${this.API_BASE}Investor/all_investors_summary/`;
            const params = new URLSearchParams();
            if (projectId) params.append('project_id', projectId);
            
            const response = await fetch(`${url}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('خطا در دریافت خلاصه سرمایه‌گذاران:', error);
            throw error;
        }
    }

    /**
     * دریافت آمار تفصیلی تراکنش‌ها
     */
    async getTransactionStatistics(projectId = null, filters = {}) {
        const cacheKey = `transaction_statistics_${projectId || 'active'}_${JSON.stringify(filters)}`;
        
        if (this.isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).data;
        }

        try {
            const url = `${this.API_BASE}Transaction/detailed_statistics/`;
            const params = new URLSearchParams();
            if (projectId) params.append('project_id', projectId);
            
            // اضافه کردن فیلترها
            Object.keys(filters).forEach(key => {
                if (filters[key] !== null && filters[key] !== undefined) {
                    params.append(key, filters[key]);
                }
            });
            
            const response = await fetch(`${url}?${params}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.setCache(cacheKey, data);
            return data;
            
        } catch (error) {
            console.error('خطا در دریافت آمار تراکنش‌ها:', error);
            throw error;
        }
    }

    /**
     * مدیریت کش
     */
    setCache(key, data) {
        this.cache.set(key, {
            data: data,
            timestamp: Date.now()
        });
    }

    isCacheValid(key) {
        if (!this.cache.has(key)) {
            return false;
        }
        
        const cached = this.cache.get(key);
        const now = Date.now();
        
        return (now - cached.timestamp) < this.cacheTimeout;
    }

    clearCache() {
        this.cache.clear();
    }

    /**
     * فرمت اعداد
     */
    formatNumber(number, decimalPlaces = 2) {
        return new Intl.NumberFormat('en-US', {
            minimumFractionDigits: decimalPlaces,
            maximumFractionDigits: decimalPlaces
        }).format(number);
    }

    /**
     * فرمت درصد
     */
    formatPercentage(number, decimalPlaces = 2) {
        return `${this.formatNumber(number, decimalPlaces)}%`;
    }

    /**
     * تبدیل به تومان
     */
    convertToToman(amount) {
        return amount / 10;
    }

    /**
     * به‌روزرسانی UI با داده‌های جدید
     */
    updateUI(elementId, value, formatter = null) {
        const element = document.getElementById(elementId);
        if (element) {
            if (formatter) {
                element.textContent = formatter(value);
            } else {
                element.textContent = this.formatNumber(value);
            }
        }
    }

    /**
     * به‌روزرسانی چندین عنصر UI
     */
    updateMultipleUI(updates) {
        updates.forEach(update => {
            this.updateUI(update.id, update.value, update.formatter);
        });
    }
}

// ایجاد instance سراسری
window.financialService = new FinancialCalculationService();

/**
 * توابع کمکی برای سازگاری با کدهای موجود
 */
window.loadProjectData = async function(projectId = null) {
    try {
        const analysis = await window.financialService.getComprehensiveAnalysis(projectId);
        
        if (analysis.error) {
            console.error('خطا در دریافت داده‌های پروژه:', analysis.error);
            return null;
        }
        
        return analysis;
        
    } catch (error) {
        console.error('خطا در بارگذاری داده‌های پروژه:', error);
        return null;
    }
};

window.loadProfitMetrics = async function(projectId = null) {
    try {
        const metrics = await window.financialService.getProfitMetrics(projectId);
        
        if (metrics.error) {
            console.error('خطا در دریافت متریک‌های سود:', metrics.error);
            return null;
        }
        
        return metrics;
        
    } catch (error) {
        console.error('خطا در بارگذاری متریک‌های سود:', error);
        return null;
    }
};

window.loadCostMetrics = async function(projectId = null) {
    try {
        const metrics = await window.financialService.getCostMetrics(projectId);
        
        if (metrics.error) {
            console.error('خطا در دریافت متریک‌های هزینه:', metrics.error);
            return null;
        }
        
        return metrics;
        
    } catch (error) {
        console.error('خطا در بارگذاری متریک‌های هزینه:', error);
        return null;
    }
};

window.loadInvestorData = async function(investorId, projectId = null) {
    try {
        const [statistics, ratios] = await Promise.all([
            window.financialService.getInvestorStatistics(investorId, projectId),
            window.financialService.getInvestorRatios(investorId, projectId)
        ]);
        
        if (statistics.error || ratios.error) {
            console.error('خطا در دریافت داده‌های سرمایه‌گذار:', statistics.error || ratios.error);
            return null;
        }
        
        return {
            statistics: statistics,
            ratios: ratios
        };
        
    } catch (error) {
        console.error('خطا در بارگذاری داده‌های سرمایه‌گذار:', error);
        return null;
    }
};

// Export برای استفاده در ماژول‌ها
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FinancialCalculationService;
}
