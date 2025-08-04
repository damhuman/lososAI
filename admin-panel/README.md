# Seafood Store Admin Panel

A modern React-based admin panel for managing the seafood store with full CRUD operations, S3 image uploads, and comprehensive reporting.

## Features

- 🏪 **Categories Management**: Add, edit, delete product categories with descriptions and icons
- 🐟 **Products Management**: Full product management with S3 image uploads and package management
- 👥 **Users Management**: View and manage Telegram bot users with gold client status
- 📦 **Orders Management**: View orders, update status, and export Excel reports
- 📊 **Dashboard**: Real-time statistics and charts
- 🏢 **Settings**: Manage delivery districts and promo codes
- 🔐 **Authentication**: JWT-based admin authentication
- 📱 **Responsive**: Works on desktop and mobile devices

## Technology Stack

- **Frontend**: React 18 with TypeScript
- **UI Library**: Ant Design 5.x
- **State Management**: React Query for server state
- **Charts**: Recharts for data visualization
- **File Upload**: Direct S3 integration via backend API
- **Authentication**: JWT tokens with automatic refresh

## Development

### Prerequisites

- Node.js 16+ and npm
- Backend API running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The admin panel will be available at http://localhost:3000

### Building for Production

```bash
# Build for production
npm run build

# The build files will be in the 'build' directory
```

## Configuration

The admin panel is configured to work with the backend API through proxy settings in package.json. In production, it's served directly by the FastAPI backend at `/adminpanel`.

### Environment Variables

Create a `.env` file in the admin-panel directory if needed:

```
REACT_APP_API_URL=/api/v1
```

## Authentication

Default admin credentials:
- Username: `admin`
- Password: As configured in backend `.env` file (`ADMIN_PASSWORD`)

## API Integration

The admin panel integrates with the following backend endpoints:

- `/api/v1/admin/login` - Authentication
- `/api/v1/admin/categories` - Categories CRUD
- `/api/v1/admin/products` - Products CRUD
- `/api/v1/admin/users` - Users management
- `/api/v1/admin/orders` - Orders management
- `/api/v1/admin/upload/image` - S3 image upload
- `/api/v1/admin/districts` - Delivery districts
- `/api/v1/admin/promo-codes` - Promo codes management

## File Upload

Images are automatically uploaded to DigitalOcean Spaces (S3-compatible) with:
- Automatic resizing and optimization
- JPG conversion for consistency
- Unique filename generation
- Public URL generation

## Deployment

The admin panel is automatically built and served by the FastAPI backend when the `build` directory exists. The backend serves it at `/adminpanel` with SPA routing support.

## Security

- JWT token-based authentication
- Automatic token refresh
- Protected routes
- CORS protection
- File upload validation

## Support

For issues or questions, check the main project documentation or create an issue in the project repository.