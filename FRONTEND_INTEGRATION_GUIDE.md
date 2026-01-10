# 🌱 Plant Doctor - Frontend Integration Guide

## Complete API Documentation for Frontend Development

**Base URL:** `http://localhost:8000/api/v1`  
**API Version:** v1  
**Content-Type:** `application/json` (except file uploads)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Error Handling](#error-handling)
4. [API Endpoints](#api-endpoints)
   - [Auth Endpoints](#auth-endpoints)
   - [Diagnosis Endpoints](#diagnosis-endpoints)
   - [Farm Endpoints](#farm-endpoints)
   - [Routine Checks Endpoints](#routine-checks-endpoints)
5. [Data Models](#data-models)
6. [Enums & Constants](#enums--constants)
7. [Integration Examples](#integration-examples)
8. [Recommended App Screens](#recommended-app-screens)

---

## Overview

Plant Doctor is an AI-powered plant disease diagnosis app that:
- 🔍 Analyzes plant leaf images to detect diseases
- 🌾 Supports tomato, potato, and pepper crops
- 📅 Provides routine care reminders and schedules
- 📊 Tracks diagnosis history for authenticated users

### Supported Crops & Diseases

| Crop | Diseases Detected |
|------|-------------------|
| 🍅 Tomato | Early Blight, Late Blight, Bacterial Spot, Leaf Mold, Septoria Leaf Spot, Target Spot, Mosaic Virus, Yellow Leaf Curl Virus, Spider Mites, Healthy |
| 🥔 Potato | Early Blight, Late Blight, Healthy |
| 🌶️ Pepper | Bacterial Spot, Healthy |

---

## Authentication

### JWT Token Authentication

The API uses JWT (JSON Web Token) for authentication.

**Token Types:**
- **Access Token:** Short-lived (30 minutes), used for API requests
- **Refresh Token:** Long-lived (7 days), used to get new access tokens

### How to Use Tokens

Include the access token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Token Flow

```
1. User registers/logs in → Get access_token + refresh_token
2. Store both tokens securely (encrypted storage)
3. Use access_token for all API requests
4. When access_token expires (401 error) → Call /auth/refresh
5. If refresh fails → Redirect to login
```

---

## Error Handling

### Standard Error Response

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {
      "errors": [
        {
          "field": "email",
          "message": "value is not a valid email address",
          "type": "value_error"
        }
      ]
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 201 | Created | Resource created successfully |
| 204 | No Content | Success, no response body |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Token expired/invalid → Refresh or login |
| 403 | Forbidden | Not allowed to access this resource |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (email/username exists) |
| 422 | Validation Error | Check field requirements |
| 500 | Server Error | Retry or contact support |
| 503 | Service Unavailable | Model not loaded, retry later |

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Request validation failed |
| `EMAIL_EXISTS` | Email already registered |
| `USERNAME_EXISTS` | Username already taken |
| `INVALID_CREDENTIALS` | Wrong email/password |
| `TOKEN_EXPIRED` | JWT token has expired |
| `TOKEN_INVALID` | JWT token is malformed |
| `NOT_FOUND` | Resource not found |

---

## API Endpoints

### Auth Endpoints

#### POST `/auth/register` - Register New User

Creates a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "SecurePass123",
  "full_name": "John Doe"  // optional
}
```

**Validation Rules:**
- `email`: Valid email format, unique
- `username`: 3-100 chars, letters/numbers/underscores/hyphens only, unique
- `password`: Min 8 chars, must include: 1 uppercase, 1 lowercase, 1 digit
- `full_name`: Optional, max 255 chars

**Response (201):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2026-01-10T10:30:00.000Z",
  "updated_at": null
}
```

**Errors:**
- `409` - Email or username already exists

---

#### POST `/auth/login` - User Login

Authenticates user and returns tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Errors:**
- `401` - Invalid credentials

---

#### POST `/auth/refresh` - Refresh Access Token

Get a new access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

#### GET `/auth/me` - Get Current User Profile

🔒 **Requires Authentication**

**Response (200):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2026-01-10T10:30:00.000Z",
  "updated_at": "2026-01-10T12:00:00.000Z"
}
```

---

#### PUT `/auth/me` - Update User Profile

🔒 **Requires Authentication**

**Request Body (all fields optional):**
```json
{
  "email": "newemail@example.com",
  "username": "new_username",
  "full_name": "New Name"
}
```

**Response (200):** Updated user object

---

#### POST `/auth/change-password` - Change Password

🔒 **Requires Authentication**

**Request Body:**
```json
{
  "current_password": "OldPass123",
  "new_password": "NewSecure456"
}
```

**Response:** `204 No Content`

---

### Diagnosis Endpoints

#### POST `/diagnosis/predict` - Diagnose Plant Disease 🌟

**Main Feature** - Upload plant leaf image for AI diagnosis.

🔓 **Authentication Optional** (but required to save history)

**Request:**
- Content-Type: `multipart/form-data`
- Field: `image` (file) - JPEG, PNG, or other image formats

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/diagnosis/predict" \
  -H "Authorization: Bearer <token>" \
  -F "image=@plant_leaf.jpg"
```

**JavaScript/Fetch Example:**
```javascript
const formData = new FormData();
formData.append('image', imageFile);

const response = await fetch('/api/v1/diagnosis/predict', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`  // Optional
  },
  body: formData
});
```

**Response (200):**
```json
{
  "success": true,
  "diagnosis": {
    "disease_name": "Early Blight",
    "confidence": 0.95,
    "is_healthy": false,
    "detected_crop": "tomato",
    "description": "Early blight is a fungal disease causing dark spots with concentric rings on older leaves...",
    "treatment": "Remove infected leaves immediately. Apply copper-based fungicide...",
    "prevention": "Rotate crops every 2-3 years. Water at base of plants..."
  },
  "recommendations": [
    "Remove and destroy infected leaves",
    "Apply fungicide treatment",
    "Improve air circulation"
  ],
  "message": "Diagnosis completed successfully"
}
```

**Errors:**
- `400` - File must be an image
- `503` - Model not loaded

---

#### GET `/diagnosis/history` - Get Diagnosis History

🔒 **Requires Authentication**

**Response (200):**
```json
{
  "total_diagnoses": 15,
  "healthy_count": 10,
  "diseased_count": 5,
  "diagnoses": [
    {
      "id": 1,
      "image_url": "/uploads/abc123.jpg",
      "disease_name": "Early Blight",
      "confidence": 0.95,
      "is_healthy": false,
      "detected_crop": "tomato",
      "description": "...",
      "treatment": "...",
      "prevention": "...",
      "user_id": 1,
      "created_at": "2026-01-10T10:30:00.000Z"
    }
  ]
}
```

---

#### GET `/diagnosis/history/{diagnosis_id}` - Get Specific Diagnosis

🔒 **Requires Authentication**

**Response (200):** Single diagnosis object

---

#### GET `/diagnosis/diseases` - List Supported Diseases

🔓 **Public**

**Response (200):**
```json
[
  {
    "class_name": "Tomato_Early_Blight",
    "plant_type": "Tomato",
    "is_disease": true
  },
  {
    "class_name": "Tomato_healthy",
    "plant_type": "Tomato",
    "is_disease": false
  }
]
```

---

#### GET `/diagnosis/disease-info/{disease_class}` - Get Disease Details

🔓 **Public**

**Example:** `/diagnosis/disease-info/Tomato_Early_Blight`

**Response (200):**
```json
{
  "disease_name": "Early Blight",
  "is_healthy": false,
  "description": "Early blight is a fungal disease...",
  "treatment": "Remove infected leaves...",
  "prevention": "Rotate crops...",
  "recommendations": ["...", "..."]
}
```

---

#### GET `/diagnosis/model-status` - Check AI Model Status

🔓 **Public**

**Response (200):**
```json
{
  "model_loaded": true,
  "model_path": "/path/to/model.h5",
  "supported_classes": 16,
  "image_size": [224, 224]
}
```

---

### Farm Endpoints

#### POST `/farm/crops` - Add Crop to Farm

🔒 **Requires Authentication**

**Request Body:**
```json
{
  "crop_type": "tomato",
  "location": "North field",  // optional
  "notes": "Planted in spring"  // optional
}
```

**Response (201):**
```json
{
  "id": 1,
  "crop_type": "tomato",
  "location": "North field",
  "notes": "Planted in spring",
  "is_active": true,
  "owner_id": 1,
  "created_at": "2026-01-10T10:30:00.000Z"
}
```

---

#### GET `/farm/crops` - Get All Farm Crops

🔒 **Requires Authentication**

**Response (200):** Array of farm crops

---

#### GET `/farm/summary` - Get Farm Summary

🔒 **Requires Authentication**

**Response (200):**
```json
{
  "total_crops": 3,
  "crops": [...],
  "crop_types": ["tomato", "potato", "pepper"]
}
```

---

#### GET `/farm/crops/{crop_id}` - Get Specific Crop

🔒 **Requires Authentication**

---

#### PUT `/farm/crops/{crop_id}` - Update Crop

🔒 **Requires Authentication**

**Request Body:**
```json
{
  "location": "New location",
  "notes": "Updated notes",
  "is_active": true
}
```

---

#### DELETE `/farm/crops/{crop_id}` - Remove Crop

🔒 **Requires Authentication**

**Response:** `204 No Content`

---

#### GET `/farm/supported-crops` - List Supported Crop Types

🔓 **Public**

**Response (200):**
```json
[
  {
    "type": "tomato",
    "name": "Tomato",
    "emoji": "🍅",
    "description": "Tomato plants - detect early blight, late blight..."
  },
  {
    "type": "potato",
    "name": "Potato",
    "emoji": "🥔",
    "description": "..."
  },
  {
    "type": "pepper",
    "name": "Pepper (Bell)",
    "emoji": "🌶️",
    "description": "..."
  }
]
```

---

### Routine Checks Endpoints

#### POST `/routines/` - Create Routine Check

🔒 **Requires Authentication**

**Request Body:**
```json
{
  "title": "Water tomatoes",
  "description": "Check soil moisture and water if dry",
  "frequency": "daily",
  "check_type": "watering",
  "crop_type": "tomato",
  "next_check_date": "2026-01-11T08:00:00.000Z",
  "notes": "Morning watering preferred"
}
```

---

#### GET `/routines/` - Get All Routine Checks

🔒 **Requires Authentication**

**Query Parameters:**
- `active_only` (bool, default: true) - Only return active checks
- `crop_type` (string, optional) - Filter by crop type

**Example:** `/routines/?crop_type=tomato&active_only=true`

---

#### GET `/routines/upcoming` - Get Upcoming Checks (Grouped)

🔒 **Requires Authentication**

**Query Parameters:**
- `crop_type` (string, optional) - Filter by crop type

**Response (200):**
```json
{
  "overdue": [
    {
      "id": 1,
      "title": "Water tomatoes",
      "check_type": "watering",
      "crop_type": "tomato",
      "next_check_date": "2026-01-09T08:00:00.000Z",
      ...
    }
  ],
  "due_today": [...],
  "due_this_week": [...]
}
```

---

#### GET `/routines/notifications` - Get Push Notification Payloads 📱

🔒 **Requires Authentication**

For mobile push notifications.

**Response (200):**
```json
[
  {
    "check_id": 1,
    "title": "🍅 Tomato Care Reminder",
    "message": "Time to water your tomatoes!",
    "check_type": "watering",
    "crop_type": "tomato",
    "due_date": "2026-01-10T08:00:00.000Z",
    "is_overdue": false
  }
]
```

---

#### GET `/routines/{check_id}` - Get Specific Check

🔒 **Requires Authentication**

---

#### PUT `/routines/{check_id}` - Update Check

🔒 **Requires Authentication**

---

#### POST `/routines/{check_id}/complete` - Mark Check Complete ✅

🔒 **Requires Authentication**

**Request Body (optional):**
```json
{
  "notes": "Plants looked healthy, watered thoroughly"
}
```

**Response:** Updated routine check with new `next_check_date`

---

#### DELETE `/routines/{check_id}` - Delete Check

🔒 **Requires Authentication**

**Response:** `204 No Content`

---

## Data Models

### User
```typescript
interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;  // ISO 8601
  updated_at: string | null;
}
```

### DiagnosisResult
```typescript
interface DiagnosisResult {
  disease_name: string;
  confidence: number;  // 0.0 - 1.0
  is_healthy: boolean;
  detected_crop: string;  // "tomato" | "potato" | "pepper" | "unknown"
  description: string | null;
  treatment: string | null;
  prevention: string | null;
}
```

### FarmCrop
```typescript
interface FarmCrop {
  id: number;
  crop_type: CropType;
  location: string | null;
  notes: string | null;
  is_active: boolean;
  owner_id: number;
  created_at: string;
}
```

### RoutineCheck
```typescript
interface RoutineCheck {
  id: number;
  title: string;
  description: string | null;
  frequency: FrequencyType;
  check_type: CheckType;
  crop_type: CropType;
  next_check_date: string;
  last_check_date: string | null;
  is_active: boolean;
  user_id: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
```

---

## Enums & Constants

### CropType
```typescript
enum CropType {
  TOMATO = "tomato",
  POTATO = "potato",
  PEPPER = "pepper"
}
```

### FrequencyType
```typescript
enum FrequencyType {
  DAILY = "daily",
  WEEKLY = "weekly",
  BIWEEKLY = "biweekly",
  MONTHLY = "monthly"
}
```

### CheckType
```typescript
enum CheckType {
  WATERING = "watering",
  FERTILIZING = "fertilizing",
  PRUNING = "pruning",
  PEST_CHECK = "pest_check",
  DISEASE_CHECK = "disease_check",
  SOIL_CHECK = "soil_check",
  GENERAL = "general"
}
```

---

## Integration Examples

### React Native / Expo Example

```javascript
// api.js - API Service
const BASE_URL = 'http://localhost:8000/api/v1';

class ApiService {
  constructor() {
    this.accessToken = null;
    this.refreshToken = null;
  }

  setTokens(access, refresh) {
    this.accessToken = access;
    this.refreshToken = refresh;
    // Store in AsyncStorage for persistence
  }

  async request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle token expiration
    if (response.status === 401 && this.refreshToken) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) {
        return this.request(endpoint, options);  // Retry
      }
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error?.message || 'Request failed');
    }

    if (response.status === 204) return null;
    return response.json();
  }

  async refreshAccessToken() {
    try {
      const response = await fetch(`${BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });
      
      if (response.ok) {
        const data = await response.json();
        this.accessToken = data.access_token;
        return true;
      }
    } catch (e) {
      console.error('Token refresh failed', e);
    }
    return false;
  }

  // Auth
  async register(email, username, password, fullName) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password, full_name: fullName }),
    });
  }

  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setTokens(data.access_token, data.refresh_token);
    return data;
  }

  async getProfile() {
    return this.request('/auth/me');
  }

  // Diagnosis
  async diagnoseImage(imageUri) {
    const formData = new FormData();
    formData.append('image', {
      uri: imageUri,
      type: 'image/jpeg',
      name: 'plant.jpg',
    });

    const response = await fetch(`${BASE_URL}/diagnosis/predict`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
      },
      body: formData,
    });

    return response.json();
  }

  async getDiagnosisHistory() {
    return this.request('/diagnosis/history');
  }

  // Farm
  async addCrop(cropType, location, notes) {
    return this.request('/farm/crops', {
      method: 'POST',
      body: JSON.stringify({ crop_type: cropType, location, notes }),
    });
  }

  async getFarmCrops() {
    return this.request('/farm/crops');
  }

  // Routines
  async getUpcomingChecks(cropType) {
    const query = cropType ? `?crop_type=${cropType}` : '';
    return this.request(`/routines/upcoming${query}`);
  }

  async completeCheck(checkId, notes) {
    return this.request(`/routines/${checkId}/complete`, {
      method: 'POST',
      body: JSON.stringify({ notes }),
    });
  }

  async getNotifications() {
    return this.request('/routines/notifications');
  }
}

export default new ApiService();
```

### Usage in React Component

```jsx
import api from './api';

// Login
const handleLogin = async () => {
  try {
    await api.login(email, password);
    navigation.navigate('Home');
  } catch (error) {
    Alert.alert('Error', error.message);
  }
};

// Diagnose plant
const handleCapture = async (imageUri) => {
  setLoading(true);
  try {
    const result = await api.diagnoseImage(imageUri);
    if (result.success) {
      navigation.navigate('Results', { diagnosis: result.diagnosis });
    }
  } catch (error) {
    Alert.alert('Error', 'Failed to analyze image');
  }
  setLoading(false);
};
```

---

## Recommended App Screens

### 1. **Onboarding / Auth Flow**
- Welcome Screen
- Login Screen
- Registration Screen
- Forgot Password (future)

### 2. **Main Tabs**
- **🏠 Home/Dashboard**
  - Quick diagnosis button (camera)
  - Today's tasks summary
  - Recent diagnoses
  
- **📷 Diagnose** (Main Feature)
  - Camera view for capturing leaf images
  - Gallery picker option
  - Results screen with:
    - Disease name + confidence %
    - Healthy/Diseased indicator
    - Treatment recommendations
    - Prevention tips
    
- **🌾 My Farm**
  - List of crops user grows
  - Add new crop
  - Crop details + associated checks
  
- **📅 Routine Checks**
  - Overdue (red badges)
  - Due Today
  - Upcoming This Week
  - Mark complete flow
  - Create custom check
  
- **👤 Profile**
  - User info
  - Edit profile
  - Diagnosis history
  - Change password
  - Logout

### 3. **Supporting Screens**
- Disease Encyclopedia (browse all diseases)
- Disease Detail View
- Settings
- Notifications

---

## Other Endpoints

### Health Check

**GET** `/health`

```json
{
  "status": "I am very healthy because i was built by Mesh",
  "model_loaded": true
}
```

### Root

**GET** `/`

```json
{
  "Message": "Hi, i am Plant Doctor, built by Mesh"
}
```

### Static Files

Uploaded images are served from: `/uploads/{filename}`

Example: `http://localhost:8000/uploads/abc123.jpg`

---

## API Interactive Documentation

When running the server, access:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Notes for Frontend Developer

1. **Image Upload:** Always use `multipart/form-data` for the `/diagnosis/predict` endpoint
2. **Token Storage:** Store tokens securely (Keychain on iOS, Encrypted SharedPreferences on Android)
3. **Offline Mode:** Consider caching disease info for offline reference
4. **Error Handling:** Always handle 401 errors and trigger token refresh
5. **Loading States:** Diagnosis can take 1-3 seconds, show loading indicators
6. **Confidence Display:** Consider showing confidence as percentage (e.g., "95% confident")
7. **Push Notifications:** Poll `/routines/notifications` for background notifications

---

## Questions?

Reach out to the backend team for clarification on any endpoints.
