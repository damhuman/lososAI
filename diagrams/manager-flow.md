# Manager/Admin Flow Diagram

## Order Processing - Admin Panel & Notifications

```mermaid
flowchart TD
    Start([New Order Created]) --> Notify[Multi-Channel Notification]
    
    Notify --> TG[Telegram Notification]
    Notify --> WS[WebSocket to Admin Panel]
    Notify --> Sound[Play Casino Win Sound]
    
    WS --> AdminPanel[Admin Panel Alert]
    TG --> AdminPanel
    Sound --> AdminPanel
    
    AdminPanel --> OpenVerify[Manager Opens Verification Screen]
    OpenVerify --> PickList[Display Pick List<br/>Side-by-Side Table]
    
    PickList --> CollectItems[Manager Collects Physical Items]
    CollectItems --> UpdateWeights[Enter Actual Weights/Quantities]
    
    UpdateWeights --> LiveCalc[Real-time Price Recalculation]
    LiveCalc --> CheckThreshold{Price Difference<br/>< 10% Threshold?}
    
    CheckThreshold -->|Yes| AutoProceed[Auto-Proceed with Actual Data]
    CheckThreshold -->|No| ManualDecision{Manager Decision Required}
    
    AutoProceed --> ConfirmOrder[Confirm with Actual Data]
    
    ManualDecision -->|Confirm| ConfirmOrder
    ManualDecision -->|Cancel| CancelOrder[Cancel Order]
    
    ConfirmOrder --> UpdateDB[Update Order in Database]
    CancelOrder --> UpdateDBCancel[Mark Order Cancelled]
    
    UpdateDB --> NotifyCustomerActual[Notify Customer with Actual Details]
    UpdateDBCancel --> NotifyCancel[Notify Customer - Cancelled]
    
    NotifyCustomerActual --> AddQueue
    AddQueue --> DeliveryList[Show in Delivery Queue]
    
    DeliveryList --> ProcessDelivery[Manager Processes Delivery]
    ProcessDelivery --> MarkDelivering[Status: Delivering]
    MarkDelivering --> CompleteDelivery[Complete Delivery]
    CompleteDelivery --> MarkDelivered[Status: Delivered]
    
    MarkDelivered --> WaitDay[Wait 1 Day<br/>Configurable]
    WaitDay --> SendFeedback[Send Feedback Request]
    SendFeedback --> CollectRating[Collect 1-5 Stars]
    
    CollectRating --> CheckRating{Rating < 5?}
    CheckRating -->|Yes| AskDetails[Ask What Was Wrong]
    CheckRating -->|No| ThankYou[Thank Customer]
    
    AskDetails --> StoreFeedback[Store Feedback]
    ThankYou --> End([Process Complete])
    StoreFeedback --> End
    
    NotifyCancel --> End
    
    style Start fill:#ffe0b2
    style AutoProceed fill:#c8e6c9
    style CancelOrder fill:#ffcdd2
    style CheckThreshold fill:#fff9c4
    style MarkDelivered fill:#c8e6c9
    style End fill:#e1f5fe
```

## Verification Screen Detail

```mermaid
flowchart LR
    subgraph Verification Table
        direction TB
        Header[Order #123 - Verification]
        
        subgraph Items
            Item1["`**Salmon Fillet**
            Expected: 1.0 kg | Actual: [0.95]
            Price: 500 грн → 475 грн`"]
            
            Item2["`**Shrimp Large**
            Expected: 0.5 kg | Actual: [0.48]
            Price: 300 грн → 288 грн`"]
            
            Item3["`**Caviar Red**
            Expected: 100 g | Actual: [100]
            Price: 800 грн → 800 грн`"]
        end
        
        Total["`**Total**
        Expected: 1600 грн
        Actual: 1563 грн
        Difference: -37 грн (-2.3%)`"]
        
        Buttons[Confirm Order | Cancel Order]
    end
```

## Admin Configuration Flow

```mermaid
flowchart TD
    AdminLogin([Admin Login]) --> Dashboard[Admin Dashboard]
    
    Dashboard --> Settings[Settings Management]
    
    Settings --> AutoConfig{Configure Auto-Confirmation}
    AutoConfig --> SetThreshold[Set Price Threshold %<br/>Default: 10%]
    AutoConfig --> ToggleMode[Toggle Auto/Manual Mode]
    
    Settings --> NotifyConfig{Configure Notifications}
    NotifyConfig --> SoundSettings[Notification Sounds]
    NotifyConfig --> ChannelSettings[Notification Channels]
    
    Settings --> FeedbackConfig{Configure Feedback}
    FeedbackConfig --> SetTiming[Set Feedback Delay<br/>Default: Next Day]
    FeedbackConfig --> SetQuestions[Configure Questions]
    
    SetThreshold --> SaveConfig[Save Configuration]
    ToggleMode --> SaveConfig
    SoundSettings --> SaveConfig
    ChannelSettings --> SaveConfig
    SetTiming --> SaveConfig
    SetQuestions --> SaveConfig
    
    SaveConfig --> ApplyBusiness[Apply Business-Wide]
    
    style AdminLogin fill:#f3e5f5
    style SaveConfig fill:#c8e6c9
```

## Real-time Notification Sequence

```mermaid
sequenceDiagram
    participant C as Customer
    participant B as Backend
    participant WS as WebSocket Server
    participant AP as Admin Panel
    participant T as Telegram Bot
    participant M as Manager
    
    C->>B: Submit Order
    B->>B: Process & Save Order
    
    par Parallel Notifications
        B->>WS: Emit New Order Event
        WS->>AP: Push Notification
        AP->>AP: Show Alert + Sound
        AP->>M: Visual + Audio Alert
    and
        B->>T: Send Admin Message
        T->>M: Telegram Notification
    end
    
    M->>AP: Open Order Details
    
    M->>AP: Enter Actual Weights
    AP->>B: Calculate New Price
    B-->>AP: Updated Totals
    
    alt Price Difference < Threshold
        AP->>AP: Auto-Proceed
        AP->>B: Update Order with Actual Data
        B->>C: Send Confirmation
    else Price Difference > Threshold
        AP->>M: Show Confirmation Required
        M->>AP: Confirm/Cancel Decision
        AP->>B: Update Order Status
        B->>C: Send Updated Confirmation
    end
```

## Order Status State Machine

```mermaid
stateDiagram-v2
    [*] --> Pending: Order Created
    
    Pending --> Verification: Manager Opens Order
    
    Verification --> Weighing: Manager Weighs Items
    Weighing --> PriceCalculated: Enter Actual Weights
    
    PriceCalculated --> AutoConfirmed: Difference < Threshold
    PriceCalculated --> ManualConfirm: Difference > Threshold
    
    AutoConfirmed --> Confirmed
    ManualConfirm --> Confirmed: Manager Confirms
    ManualConfirm --> Cancelled: Manager Cancels
    
    Confirmed --> Preparing: Start Preparation
    Preparing --> Delivering: Out for Delivery
    Delivering --> Delivered: Completed
    
    Delivered --> FeedbackPending: After Delay
    FeedbackPending --> FeedbackReceived: Customer Responds
    FeedbackPending --> FeedbackSkipped: No Response
    
    FeedbackReceived --> [*]
    FeedbackSkipped --> [*]
    Cancelled --> [*]
    
    note right of PriceCalculated
        System checks if price
        difference is within
        configured threshold
    end note
    
    note right of AutoConfirmed
        Auto-proceeds when
        difference < 10%
    end note
    
    note right of ManualConfirm
        Manager must confirm
        when difference > 10%
    end note
```