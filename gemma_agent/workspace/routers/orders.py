from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from .. import database, models

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=models.OrderResponse, status_code=201)
def create_order(order_data: models.OrderCreate, db=Depends(database.get_db)):
    """
    Create a new order.
    """
    order_id = f"ORD-{len(db['orders']) + 1}"
    total_amount = 0.0
    
    # Calculate total amount
    for item in order_data.items:
        menu_item = db['menu'].get(item.menu_item_id)
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {item.menu_item_id} not found")
        
        # Ensure price consistency (though we use price_at_order from request, we validate against menu)
        if abs(menu_item['price'] - item.price_at_order) > 0.01:
             raise HTTPException(status_code=400, detail="Price mismatch between menu and order")

        total_amount += menu_item['price'] * item.quantity

    # Create order response object
    order_response = models.OrderResponse(
        order_id=order_id,
        customer_name=order_data.customer_name,
        customer_phone=order_data.customer_phone,
        delivery_address=order_data.delivery_address,
        items=[
            models.OrderItem(
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
                price_at_order=item.price_at_order
            ) for item in order_data.items
        ],
        total_amount=total_amount,
        status=models.OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    # Store order
    db['orders'][order_id] = order_response.dict()
    print(f"Order {order_id} created successfully.")
    return order_response

@router.get("/{order_id}", response_model=models.TrackingResponse)
def get_order_status(order_id: str, db=Depends(database.get_db)):
    """
    Get the current status and tracking information for an order.
    """
    order = db['orders'].get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Convert dict back to Pydantic model for response
    return models.TrackingResponse(
        order_id=order_id,
        status=models.OrderStatus(order['status']),
        last_updated=order['updated_at'],
        tracking_info=order.get('tracking_number')
    )

@router.patch("/{order_id}/status", response_model=models.TrackingResponse)
def update_order_status(order_id: str, update_data: models.OrderUpdate, db=Depends(database.get_db)):
    """
    Update the status of an order (e.g., PENDING -> PREPARING).
    """
    order = db['orders'].get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    new_status = update_data.status
    
    # Simple state machine logic (can be expanded)
    current_status = models.OrderStatus(order['status'])
    
    if current_status == models.OrderStatus.DELIVERED or current_status == models.OrderStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Order is already finalized.")

    # Basic transition validation
    valid_transitions = {
        models.OrderStatus.PENDING: [models.OrderStatus.PREPARING, models.OrderStatus.CANCELLED],
        models.OrderStatus.PREPARING: [models.OrderStatus.READY, models.OrderStatus.CANCELLED],
        models.OrderStatus.READY: [models.OrderStatus.OUT_FOR_DELIVERY, models.OrderStatus.CANCELLED],
        models.OrderStatus.OUT_FOR_DELIVERY: [models.OrderStatus.DELIVERED]
    }

    if new_status not in valid_transitions.get(current_status, []):
        raise HTTPException(status_code=400, detail=f"Invalid status transition from {current_status.value} to {new_status.value}")

    # Update order
    order['status'] = new_status.value
    order['updated_at'] = datetime.now()
    if update_data.tracking_number:
        order['tracking_number'] = update_data.tracking_number
    
    print(f"Order {order_id} status updated to {new_status.value}")
    return models.TrackingResponse(
        order_id=order_id,
        status=new_status,
        last_updated=datetime.now(),
        tracking_info=order.get('tracking_number')
    )

# Note: In a real app, we would also have endpoints for menu management, user authentication, etc.
