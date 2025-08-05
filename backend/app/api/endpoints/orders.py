from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload

from app.api.deps import get_async_session, get_current_user
from app.db.models.user import User
from app.db.models.order import Order, OrderItem, OrderStatus, DeliveryTimeSlot
from app.db.models.product import District, PromoCode, Product
from app.schemas.order import OrderCreate, Order as OrderSchema, OrderSummary
from app.services.messaging import messaging_service

router = APIRouter()


async def get_next_order_id(session: AsyncSession) -> int:
    """Get the next order ID starting from 100"""
    result = await session.execute(
        select(func.max(Order.order_id))
    )
    max_order_id = result.scalar()
    
    if max_order_id is None:
        return 100
    else:
        return max_order_id + 1


@router.post("/", response_model=OrderSchema)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Create a new order"""
    print(f"🚀 Order creation started for user {current_user.id} ({current_user.first_name})")
    print(f"📊 Order data: {len(order_data.items)} items, total: {order_data.total}")
    
    # Validate district
    district_name = order_data.delivery.get("district")
    if not district_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="District is required"
        )
    
    district_result = await session.execute(
        select(District).where(
            District.name == district_name,
            District.is_active == True
        )
    )
    district = district_result.scalar_one_or_none()
    
    if not district:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid district"
        )
    
    # Parse delivery time slot
    time_slot_str = order_data.delivery.get("time_slot")
    time_slot_map = {
        "morning": DeliveryTimeSlot.MORNING,
        "afternoon": DeliveryTimeSlot.AFTERNOON,
        "evening": DeliveryTimeSlot.EVENING
    }
    
    delivery_time_slot = time_slot_map.get(time_slot_str)
    if not delivery_time_slot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid delivery time slot"
        )
    
    # Calculate delivery date (next day if ordered before 18:00)
    now = datetime.now()
    if now.hour < 18:
        delivery_date = now.date() + timedelta(days=1)
    else:
        delivery_date = now.date() + timedelta(days=2)
    
    delivery_datetime = datetime.combine(delivery_date, datetime.min.time())
    
    # Validate promo code if provided
    discount_amount = 0
    is_gold_client = current_user.is_gold_client
    
    if order_data.promo_code:
        promo_result = await session.execute(
            select(PromoCode).where(
                PromoCode.code == order_data.promo_code,
                PromoCode.is_active == True
            )
        )
        promo = promo_result.scalar_one_or_none()
        
        if promo:
            # Check usage limit
            if promo.usage_limit and promo.usage_count >= promo.usage_limit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Promo code usage limit exceeded"
                )
            
            # Apply discount
            if promo.discount_percent > 0:
                discount_amount = order_data.total * (promo.discount_percent / 100)
            elif promo.discount_amount > 0:
                discount_amount = promo.discount_amount
            
            # Mark as gold client if applicable
            if promo.is_gold_code:
                is_gold_client = True
                current_user.is_gold_client = True
            
            # Update promo usage
            promo.usage_count += 1
    
    # Get next order ID
    next_order_id = await get_next_order_id(session)
    
    # Create order
    order = Order(
        user_id=current_user.id,
        order_id=next_order_id,
        status=OrderStatus.PENDING,
        total_amount=order_data.total - discount_amount,
        promo_code_used=order_data.promo_code,
        discount_amount=discount_amount,
        district_id=district.id,
        delivery_time_slot=delivery_time_slot,
        delivery_date=delivery_datetime,
        comment=order_data.delivery.get("comment"),
        contact_name=order_data.user_name,
        contact_phone=current_user.phone
    )
    
    session.add(order)
    await session.flush()  # Get order ID
    
    # Validate products and create order items
    for item_data in order_data.items:
        # Validate product exists
        product_result = await session.execute(
            select(Product).where(
                Product.id == item_data.product_id,
                Product.is_active == True
            )
        )
        product = product_result.scalar_one_or_none()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product {item_data.product_id} not found or inactive"
            )
        
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data.product_id,
            product_name=item_data.product_name,
            package_id=item_data.package_id,
            weight=item_data.weight,
            unit=item_data.unit,
            quantity=item_data.quantity,
            price_per_unit=item_data.price_per_unit,
            total_price=item_data.total_price
        )
        session.add(order_item)
    
    await session.commit()
    await session.refresh(order)
    
    # Load relationships
    await session.refresh(order, ["items", "district"])
    
    # Send confirmation messages
    try:
        print(f"📤 Sending order confirmation messages for order #{order.order_id}")
        
        # Send confirmation to client
        client_result = await messaging_service.send_order_confirmation_to_client(order)
        print(f"📱 Client message result: {client_result}")
        
        # Send notification to admin
        admin_result = await messaging_service.send_order_notification_to_admin(order)
        print(f"👨‍💼 Admin message result: {admin_result}")
        
    except Exception as e:
        # Log error but don't fail the order creation
        print(f"💥 Error sending order messages: {e}")
        import traceback
        traceback.print_exc()
    
    return order


@router.get("/", response_model=List[OrderSummary])
async def get_user_orders(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get current user's orders"""
    query = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )
    
    result = await session.execute(query)
    orders = result.scalars().all()
    
    # Convert to OrderSummary
    order_summaries = []
    for order in orders:
        # Count items
        items_count_query = select(func.sum(OrderItem.quantity)).where(OrderItem.order_id == order.id)
        items_count_result = await session.execute(items_count_query)
        items_count = items_count_result.scalar() or 0
        
        order_summaries.append(OrderSummary(
            id=order.id,
            order_id=order.order_id,
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount,
            delivery_date=order.delivery_date,
            contact_name=order.contact_name,
            created_at=order.created_at,
            items_count=int(items_count)
        ))
    
    return order_summaries


@router.get("/{order_id}", response_model=OrderSchema)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """Get specific order details"""
    query = (
        select(Order)
        .options(selectinload(Order.items), selectinload(Order.district))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )
    
    result = await session.execute(query)
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order