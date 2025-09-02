/**
 * Setup file for Jest tests
 */

// Mock global objects
global.console = {
  log: jest.fn(),
  error: jest.fn(),
  warn: jest.fn(),
  info: jest.fn(),
  debug: jest.fn()
};

// Mock fetch
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock sessionStorage
const sessionStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.sessionStorage = sessionStorageMock;

// Mock window.location
delete window.location;
window.location = {
  href: 'http://localhost:8000/',
  origin: 'http://localhost:8000',
  pathname: '/',
  search: '',
  hash: '',
  assign: jest.fn(),
  replace: jest.fn(),
  reload: jest.fn()
};

// Mock window.alert
window.alert = jest.fn();

// Mock window.confirm
window.confirm = jest.fn(() => true);

// Mock window.prompt
window.prompt = jest.fn();

// Mock document.cookie
Object.defineProperty(document, 'cookie', {
  writable: true,
  value: 'csrftoken=test-token'
});

// Mock jQuery
global.$ = jest.fn(() => ({
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
  find: jest.fn(() => global.$()),
  closest: jest.fn(() => global.$()),
  transition: jest.fn(),
  toast: jest.fn(),
  each: jest.fn(),
  length: 0
}));

// Mock persianDate
global.persianDate = jest.fn(() => ({
  format: jest.fn(() => '1404-06-01'),
  togregorian: jest.fn(() => new Date('2025-08-23'))
}));

// Mock Tabulator
global.Tabulator = jest.fn(() => ({
  setData: jest.fn(),
  getData: jest.fn(() => []),
  clearFilter: jest.fn(),
  setFilter: jest.fn(),
  download: jest.fn(),
  on: jest.fn()
}));

// Mock Semantic UI
global.semantic = {
  dropdown: jest.fn(),
  modal: jest.fn(),
  toast: jest.fn()
};

// Setup test utilities
global.testUtils = {
  createMockElement: (tag = 'div') => ({
    tagName: tag.toUpperCase(),
    className: '',
    innerHTML: '',
    textContent: '',
    value: '',
    style: { display: 'none' },
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(() => false),
      toggle: jest.fn()
    },
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    querySelector: jest.fn(),
    querySelectorAll: jest.fn(() => []),
    getAttribute: jest.fn(),
    setAttribute: jest.fn(),
    appendChild: jest.fn(),
    removeChild: jest.fn()
  }),
  
  createMockFormData: () => ({
    investor: '16',
    project: '1',
    period: '26',
    transaction_type: 'principal_deposit',
    amount: '10000',
    date_shamsi: '1404-06-01',
    description: 'Test transaction'
  }),
  
  mockApiResponse: (data, status = 200) => ({
    ok: status >= 200 && status < 300,
    status: status,
    json: jest.fn().mockResolvedValue(data),
    text: jest.fn().mockResolvedValue(JSON.stringify(data))
  })
};

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  localStorageMock.clear();
  sessionStorageMock.clear();
});
