import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');

// Test configuration
export let options = {
  stages: [
    // Fast 2-minute demo - jump quickly to scaling load
    { duration: '10s', target: 60 },   // Quick ramp to 60 users (should trigger HPA fast)
    { duration: '1m', target: 100 },   // Peak load - 100 users for 1m (ensure scaling)
    { duration: '30s', target: 120 },  // Maximum load to show full scaling
    { duration: '20s', target: 0 },    // Quick ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'], // 95% of requests should be below 1s (more realistic)
    http_req_failed: ['rate<0.2'],     // Error rate should be below 20% (allows for scaling delays)
  },
};

// Base URL - consistent port-forward URL
const BASE_URL = 'http://localhost:8080';

// Sample data for creating resources
const sampleCustomer = {
  name: 'Test Customer',
  email: `test${Math.random()}@example.com`,
  phone: '+1234567890'
};

const sampleProduct = {
  name: `Product ${Math.random()}`,
  price: Math.floor(Math.random() * 100) + 10,
  description: 'Test product for load testing'
};

export default function () {
  // Test 1: Health check (lightweight)
  let healthResponse = http.get(`${BASE_URL}/health`);
  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
  });

  // Test 2: Root endpoint
  let rootResponse = http.get(`${BASE_URL}/`);
  check(rootResponse, {
    'root status is 200': (r) => r.status === 200,
  });

  // Test 3: Get whoami (shows which pod is responding)
  let whoamiResponse = http.get(`${BASE_URL}/whoami`);
  check(whoamiResponse, {
    'whoami status is 200': (r) => r.status === 200,
  });

  // Test 4: List products (database read operation)
  let productsResponse = http.get(`${BASE_URL}/products/`);
  check(productsResponse, {
    'products list status is 200': (r) => r.status === 200,
  });

  // Test 5: List customers (database read operation)
  let customersResponse = http.get(`${BASE_URL}/customers/`);
  check(customersResponse, {
    'customers list status is 200': (r) => r.status === 200,
  });

  // Test 6: List orders (database read operation)
  let ordersResponse = http.get(`${BASE_URL}/orders/`);
  check(ordersResponse, {
    'orders list status is 200': (r) => r.status === 200,
  });

  // Test 7: Create customer (database write operation - more CPU intensive)
  if (Math.random() < 0.3) { // 30% chance to create a customer
    let createCustomerResponse = http.post(
      `${BASE_URL}/customers/`,
      JSON.stringify(sampleCustomer),
      { headers: { 'Content-Type': 'application/json' } }
    );
    check(createCustomerResponse, {
      'create customer status is 200': (r) => r.status === 200,
    });
  }

  // Test 8: Create product (database write operation - more CPU intensive)
  if (Math.random() < 0.2) { // 20% chance to create a product
    let createProductResponse = http.post(
      `${BASE_URL}/products/`,
      JSON.stringify(sampleProduct),
      { headers: { 'Content-Type': 'application/json' } }
    );
    check(createProductResponse, {
      'create product status is 200': (r) => r.status === 200,
    });
  }

  // Record errors
  errorRate.add(
    healthResponse.status !== 200 ||
    rootResponse.status !== 200 ||
    whoamiResponse.status !== 200 ||
    productsResponse.status !== 200 ||
    customersResponse.status !== 200 ||
    ordersResponse.status !== 200
  );

  // Small delay between requests to simulate real user behavior
  sleep(Math.random() * 2 + 0.5); // Random sleep between 0.5-2.5 seconds
}

// Setup function - runs once at the beginning
export function setup() {
  console.log('🚀 Starting K6 Fast Demo Load Test for HPA (2 minutes)');
  console.log('📊 Monitor HPA with: kubectl get hpa -w');
  console.log('🔍 Monitor pods with: kubectl get pods -w');
  console.log('⚡ Fast 2-Minute Demo Timeline:');
  console.log('  - 0-10s: Quick ramp to 60 users (should trigger HPA)');
  console.log('  - 10s-1m10s: 100 users (should scale to 4-6 pods)');
  console.log('  - 1m10s-1m40s: 120 users (should scale to 6-8 pods)');
  console.log('  - 1m40s-2m: Scale down to 0 users');
}

// Teardown function - runs once at the end
export function teardown() {
  console.log('✅ Load test completed!');
  console.log('🔍 Check final HPA status: kubectl get hpa');
  console.log('📊 Check final pod count: kubectl get pods');
}
