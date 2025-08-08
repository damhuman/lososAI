# User Flow Diagram

## Customer Journey - Seafood Store Mini App

```mermaid
flowchart TD
    Start([User Opens Telegram]) --> OpenBot[Open Seafood Store Bot]
    OpenBot --> ClickWebApp[Click 'Open Store' Button]
    ClickWebApp --> InitApp[App Initializes with Loading Screen]
    InitApp --> Auth{Telegram Auth Valid?}
    
    Auth -->|No| AuthError[Show Error Message]
    AuthError --> Start
    
    Auth -->|Yes| Categories[Display Categories Screen]
    
    Categories --> SelectCat{Select Category}
    SelectCat -->|Лосось| SalmonList[Show Salmon Products]
    SelectCat -->|Молюски| ShellfishList[Show Shellfish Products]
    SelectCat -->|Tom Yum| TomYumList[Show Tom Yum Products]
    SelectCat -->|Ікра| CaviarList[Show Caviar Products]
    
    SalmonList --> SelectProduct[Select Product]
    ShellfishList --> SelectProduct
    TomYumList --> SelectProduct
    CaviarList --> SelectProduct
    
    SelectProduct --> ProductDetail[Product Detail Screen]
    ProductDetail --> ChoosePackage[Select Package Size<br/>0.5kg / 1kg / etc.]
    ChoosePackage --> SetQuantity[Set Quantity 1-10]
    SetQuantity --> AddCart[Add to Cart]
    
    AddCart --> CartPopup{Success Popup}
    CartPopup -->|Continue Shopping| Categories
    CartPopup -->|Go to Cart| CartView[View Cart]
    
    CartView --> ModifyCart{Modify Cart?}
    ModifyCart -->|Update Quantity| UpdateQty[Change Item Quantity]
    ModifyCart -->|Remove Item| RemoveItem[Remove from Cart]
    ModifyCart -->|Proceed| Checkout[Checkout Screen]
    
    UpdateQty --> CartView
    RemoveItem --> CartView
    
    Checkout --> FillDelivery[Fill Delivery Form]
    FillDelivery --> SelectDistrict[Select District]
    SelectDistrict --> SelectTime[Choose Time Slot<br/>Morning/Afternoon/Evening]
    SelectTime --> AddComment[Add Comment<br/>Optional]
    AddComment --> PromoCode{Have Promo Code?}
    
    PromoCode -->|Yes| EnterPromo[Enter & Validate Promo]
    PromoCode -->|No| ReviewOrder[Review Order Screen]
    EnterPromo --> ReviewOrder
    
    ReviewOrder --> ConfirmOrder{Confirm Order?}
    ConfirmOrder -->|Edit| Checkout
    ConfirmOrder -->|Confirm| SubmitAPI[Submit to Backend API]
    
    SubmitAPI --> Processing{Processing}
    Processing -->|Success| OrderSuccess[Order Created Successfully]
    Processing -->|Error| OrderError[Show Error Message]
    
    OrderSuccess --> ClearCart[Clear Cart]
    ClearCart --> ShowBanner[Show Success Banner]
    ShowBanner --> TelegramMsg[Receive Telegram Confirmation]
    TelegramMsg --> Categories
    
    OrderError --> ReviewOrder
    
    style Start fill:#e1f5fe
    style OrderSuccess fill:#c8e6c9
    style OrderError fill:#ffcdd2
    style Processing fill:#fff3e0
    style Auth fill:#f3e5f5
```

## Key User Interactions

### Navigation Flow
- **Linear progression**: Categories → Products → Details → Cart → Checkout
- **Back navigation**: Telegram back button available at any step
- **Cart access**: Cart icon visible on all screens except loading/cart

### Decision Points
1. **Product Selection**: Browse multiple categories and products
2. **Package Choice**: Select appropriate weight/size
3. **Cart Management**: Continue shopping vs checkout
4. **Promo Code**: Optional discount application
5. **Order Confirmation**: Final review before submission

### Error Recovery
- **Auth failures**: Redirect to start
- **API errors**: Show message, allow retry
- **Validation errors**: Highlight fields, prevent submission

### Success Path
1. Browse → Select → Add to Cart → Checkout → Confirm → Success
2. Minimum steps: 7 (direct path)
3. Average steps: 10-12 (with browsing)

## Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant W as WebApp
    participant B as Backend API
    participant T as Telegram Bot
    participant A as Admin
    
    U->>W: Open Mini App
    W->>B: Validate Auth
    B-->>W: User Authenticated
    
    U->>W: Browse Products
    W->>B: Get Categories/Products
    B-->>W: Product Data
    
    U->>W: Add to Cart
    W->>W: Update LocalStorage
    
    U->>W: Checkout
    W->>B: Submit Order
    B->>B: Process Order
    B->>T: Send Confirmations
    T-->>U: Order Confirmation
    T-->>A: Admin Notification
    B-->>W: Order Success
    
    W->>U: Show Success
```