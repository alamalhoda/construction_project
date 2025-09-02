/**
 * تست‌های JavaScript برای فرم تراکنش
 */

// Mock functions برای تست
const mockConsole = {
    log: jest.fn(),
    error: jest.fn(),
    warn: jest.fn()
};

// Mock jQuery
const mockJQuery = {
    ready: jest.fn((callback) => callback()),
    dropdown: jest.fn(),
    modal: jest.fn(),
    val: jest.fn(),
    text: jest.fn(),
    html: jest.fn(),
    addClass: jest.fn(),
    removeClass: jest.fn(),
    on: jest.fn(),
    off: jest.fn(),
    find: jest.fn(() => mockJQuery),
    closest: jest.fn(() => mockJQuery),
    transition: jest.fn(),
    toast: jest.fn()
};

// Mock fetch
global.fetch = jest.fn();

// Mock document
global.document = {
    getElementById: jest.fn(() => ({
        value: '',
        textContent: '',
        style: { display: 'none' },
        classList: {
            add: jest.fn(),
            remove: jest.fn(),
            contains: jest.fn(() => false)
        }
    })),
    querySelector: jest.fn(() => ({
        innerHTML: '',
        classList: {
            add: jest.fn(),
            remove: jest.fn()
        }
    })),
    querySelectorAll: jest.fn(() => []),
    createElement: jest.fn(() => ({
        className: '',
        innerHTML: '',
        addEventListener: jest.fn(),
        querySelector: jest.fn(() => ({
            addEventListener: jest.fn()
        }))
    })),
    cookie: 'csrftoken=test-token'
};

// Mock window
global.window = {
    addNewTransaction: jest.fn(),
    showAddTransactionModal: jest.fn(),
    closeAddTransactionModal: jest.fn(),
    resetAddTransactionForm: jest.fn(),
    formatAmount: jest.fn(),
    validateAmount: jest.fn(),
    getTodayShamsi: jest.fn(() => '2025-08-23')
};

// Mock persianDate
global.persianDate = jest.fn(() => ({
    format: jest.fn(() => '1404-06-01')
}));

describe('Transaction Form Tests', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.console = mockConsole;
        global.$ = jest.fn(() => mockJQuery);
    });

    describe('formatAmount function', () => {
        test('should format Persian digits to English', () => {
            const input = {
                value: '۱۰۰۰۰'
            };
            
            window.formatAmount(input);
            
            expect(input.value).toBe('10,000');
        });

        test('should handle English digits', () => {
            const input = {
                value: '10000'
            };
            
            window.formatAmount(input);
            
            expect(input.value).toBe('10,000');
        });

        test('should limit to 12 digits', () => {
            const input = {
                value: '1234567890123'
            };
            
            window.formatAmount(input);
            
            expect(input.value).toBe('1,234,567,890,123');
        });

        test('should handle empty input', () => {
            const input = {
                value: ''
            };
            
            window.formatAmount(input);
            
            expect(input.value).toBe('');
        });
    });

    describe('validateAmount function', () => {
        test('should validate positive amounts', () => {
            const input = {
                value: '10000',
                classList: {
                    add: jest.fn(),
                    remove: jest.fn()
                }
            };
            
            window.validateAmount(input);
            
            expect(input.classList.remove).toHaveBeenCalledWith('error');
        });

        test('should mark negative amounts as error', () => {
            const input = {
                value: '-1000',
                classList: {
                    add: jest.fn(),
                    remove: jest.fn()
                }
            };
            
            window.validateAmount(input);
            
            expect(input.classList.add).toHaveBeenCalledWith('error');
        });

        test('should handle Persian digits in validation', () => {
            const input = {
                value: '۱۰۰۰۰',
                classList: {
                    add: jest.fn(),
                    remove: jest.fn()
                }
            };
            
            window.validateAmount(input);
            
            expect(input.classList.remove).toHaveBeenCalledWith('error');
        });
    });

    describe('getTodayShamsi function', () => {
        test('should return today date in Shamsi format', () => {
            const result = window.getTodayShamsi();
            
            expect(result).toBe('2025-08-23');
        });

        test('should handle persianDate not available', () => {
            global.persianDate = undefined;
            
            const result = window.getTodayShamsi();
            
            expect(result).toMatch(/^\d{4}-\d{2}-\d{2}$/);
        });
    });

    describe('addNewTransaction function', () => {
        beforeEach(() => {
            // Mock form data
            mockJQuery.val.mockImplementation((selector) => {
                const values = {
                    'addInvestorInput': '16',
                    'addProjectInput': '1',
                    'addPeriodInput': '26',
                    'addTransactionTypeInput': 'principal_deposit',
                    'addAmountInput': '10000',
                    'addDateShamsiInput': '1404-06-01',
                    'addDescriptionInput': 'Test transaction'
                };
                return values[selector] || '';
            });
        });

        test('should validate form data', () => {
            window.addNewTransaction();
            
            expect(mockConsole.log).toHaveBeenCalledWith('addNewTransaction function called');
            expect(mockConsole.log).toHaveBeenCalledWith('Starting validation...');
        });

        test('should handle validation errors', () => {
            // Mock empty form data
            mockJQuery.val.mockReturnValue('');
            
            window.addNewTransaction();
            
            expect(mockConsole.log).toHaveBeenCalledWith('Validation errors:', expect.any(Array));
        });

        test('should make API call with valid data', async () => {
            // Mock successful API response
            fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ id: 1, amount: '10000.00' })
            });

            window.addNewTransaction();
            
            // Wait for async operations
            await new Promise(resolve => setTimeout(resolve, 100));
            
            expect(fetch).toHaveBeenCalledWith(
                '/construction/api/v1/Transaction/',
                expect.objectContaining({
                    method: 'POST',
                    headers: expect.objectContaining({
                        'Content-Type': 'application/json',
                        'X-CSRFToken': 'test-token'
                    }),
                    body: expect.stringContaining('"amount":"10000"')
                })
            );
        });

        test('should handle API errors', async () => {
            // Mock API error
            fetch.mockRejectedValueOnce(new Error('Network error'));

            window.addNewTransaction();
            
            // Wait for async operations
            await new Promise(resolve => setTimeout(resolve, 100));
            
            expect(mockConsole.error).toHaveBeenCalledWith(
                'Error adding transaction:',
                expect.any(Error)
            );
        });
    });

    describe('showAddTransactionModal function', () => {
        test('should show modal and reset form', () => {
            window.showAddTransactionModal();
            
            expect(window.resetAddTransactionForm).toHaveBeenCalled();
            expect(mockJQuery.modal).toHaveBeenCalledWith('show');
        });

        test('should handle errors gracefully', () => {
            window.resetAddTransactionForm.mockImplementation(() => {
                throw new Error('Reset error');
            });

            window.showAddTransactionModal();
            
            expect(mockConsole.error).toHaveBeenCalledWith(
                'Error showing add transaction modal:',
                expect.any(Error)
            );
            expect(mockJQuery.modal).toHaveBeenCalledWith('show');
        });
    });

    describe('resetAddTransactionForm function', () => {
        test('should reset form fields', () => {
            window.resetAddTransactionModal();
            
            expect(mockJQuery.dropdown).toHaveBeenCalledWith('clear');
            expect(mockJQuery.removeClass).toHaveBeenCalledWith('error');
        });

        test('should set today date as default', () => {
            window.resetAddTransactionForm();
            
            expect(mockJQuery.val).toHaveBeenCalledWith('2025-08-23');
        });
    });
});

describe('Transaction Form Integration Tests', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        global.console = mockConsole;
        global.$ = jest.fn(() => mockJQuery);
    });

    test('should handle complete transaction workflow', async () => {
        // Mock successful API response
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ 
                id: 1, 
                amount: '10000.00',
                date_gregorian: '2025-08-23',
                day_remaining: 365,
                day_from_start: 100
            })
        });

        // Mock form data
        mockJQuery.val.mockImplementation((selector) => {
            const values = {
                'addInvestorInput': '16',
                'addProjectInput': '1',
                'addPeriodInput': '26',
                'addTransactionTypeInput': 'principal_deposit',
                'addAmountInput': '10000',
                'addDateShamsiInput': '1404-06-01',
                'addDescriptionInput': 'Integration test'
            };
            return values[selector] || '';
        });

        // Execute workflow
        window.addNewTransaction();
        
        // Wait for async operations
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Verify API call
        expect(fetch).toHaveBeenCalledWith(
            '/construction/api/v1/Transaction/',
            expect.objectContaining({
                method: 'POST',
                headers: expect.objectContaining({
                    'Content-Type': 'application/json'
                })
            })
        );
        
        // Verify success handling
        expect(mockConsole.log).toHaveBeenCalledWith('addNewTransaction function completed');
    });

    test('should handle Persian digits in complete workflow', async () => {
        // Mock successful API response
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ id: 1, amount: '10000.00' })
        });

        // Mock form data with Persian digits
        mockJQuery.val.mockImplementation((selector) => {
            const values = {
                'addInvestorInput': '16',
                'addProjectInput': '1',
                'addPeriodInput': '26',
                'addTransactionTypeInput': 'principal_deposit',
                'addAmountInput': '۱۰۰۰۰',  // Persian digits
                'addDateShamsiInput': '۱۴۰۴-۰۶-۰۱',  // Persian digits
                'addDescriptionInput': 'تست اعداد فارسی'
            };
            return values[selector] || '';
        });

        window.addNewTransaction();
        
        // Wait for async operations
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Verify that Persian digits are converted
        expect(fetch).toHaveBeenCalledWith(
            '/construction/api/v1/Transaction/',
            expect.objectContaining({
                body: expect.stringContaining('"amount":"10000"')
            })
        );
    });
});
