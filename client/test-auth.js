// Test script to verify authentication flow
console.log('Testing Authentication Flow...');

// Simulate user login
const testUser = {
  id: "test-123",
  email: "test@example.com",
  first_name: "John",
  last_name: "Doe",
  is_verified: true,
  created_at: new Date().toISOString()
};

// Store in localStorage to simulate login
localStorage.setItem('user', JSON.stringify(testUser));

// Reload page to trigger UserContext effect
window.location.reload();
