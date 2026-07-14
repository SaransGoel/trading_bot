import click
import time
from dotenv import load_dotenv

# Import our custom modules
from bot.logging_config import setup_logger
from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import (
    validate_symbol, validate_side, validate_order_type,
    validate_quantity, validate_price, InputValidationError
)

load_dotenv()
logger = setup_logger()

# --- Custom Prompt & Validation Helpers ---

def validate_levels(val):
    """Ensures basket levels are positive integers."""
    try:
        levels = int(val)
        if levels <= 0: raise ValueError
        return levels
    except:
        raise InputValidationError("Must be a positive integer.")

def safe_prompt(prompt_msg, validator, current_val=None):
    """
    Safely prompts the user, allows text-based aborts ('q', 'abort'),
    and continuously retries if the user input fails validation.
    """
    while True:
        try:
            val = click.prompt(prompt_msg, default=current_val, type=str)
            # Check for explicit abort commands
            if str(val).strip().lower() in ['q', 'abort', 'cancel', 'quit', 'exit']:
                raise click.Abort()
            return validator(val)
        except InputValidationError as e:
            click.secho(f"❌ Error: {e}", fg="red")
        except ValueError:
            click.secho("❌ Error: Invalid input type.", fg="red")

# --- Core Bot Loop ---

def run_bot():
    while True:
        click.secho("\n=========================================", fg="blue", bold=True)
        click.secho("   BINANCE FUTURES TESTNET TRADING BOT   ", fg="blue", bold=True)
        click.secho("=========================================\n", fg="blue", bold=True)
        
        click.secho("Main Menu:", fg="cyan", bold=True)
        click.secho("1. Place a New Order (Market / Limit / Stop Loss)", fg="cyan")
        click.secho("2. View & Modify an Open Limit Order", fg="cyan")
        click.secho("3. View & Cancel an Open Order", fg="cyan")
        click.secho("4. Place a Grid/Basket Order", fg="cyan")
        click.secho("5. Exit Bot", fg="red", bold=True)
        
        action = click.prompt("\nSelect an action", type=click.Choice(['1', '2', '3', '4', '5']))
        
        if action == '5':
            click.secho("\nShutting down trading bot. Goodbye!", fg="yellow", bold=True)
            break
            
        try:
            client = BinanceFuturesClient()
            manager = OrderManager(client)
            
            # ---------------------------------------------------------
            # ACTION 1: STANDARD ORDERS (WITH REVIEW/EDIT MENU)
            # ---------------------------------------------------------
            if action == '1':
                click.secho("\n--- NEW ORDER SETUP (Type 'abort' to cancel) ---", fg="cyan", bold=True)
                order = {
                    'symbol': safe_prompt('Trading Symbol (e.g., BTCUSDT)', validate_symbol),
                    'side': safe_prompt('Order Side (BUY/SELL)', validate_side),
                    'qty': safe_prompt('Quantity', validate_quantity),
                    'type': safe_prompt('Order Type (MARKET/LIMIT/STOP_MARKET)', validate_order_type),
                }
                
                if order['type'] == 'LIMIT':
                    order['price'] = safe_prompt('Limit Price', lambda x: validate_price(x, "Price"))
                elif order['type'] == 'STOP_MARKET':
                    order['stop_price'] = safe_prompt('Stop Price', lambda x: validate_price(x, "Stop Price"))

                # Review & Edit Loop
                while True:
                    click.secho("\n--- Order Summary Review ---", fg="yellow", bold=True)
                    click.echo(f"1. Symbol:      {order['symbol']}")
                    click.echo(f"2. Side:        {order['side']}")
                    click.echo(f"3. Quantity:    {order['qty']}")
                    click.echo(f"4. Type:        {order['type']}")
                    if order['type'] == 'LIMIT':
                        click.echo(f"5. Price:       {order['price']}")
                    elif order['type'] == 'STOP_MARKET':
                        click.echo(f"5. Stop Price:  {order['stop_price']}")
                        
                    click.secho("\nOptions: [E] Execute | [A] Abort | [#] Number to Edit Field", fg="cyan")
                    choice = click.prompt("Select an option", type=str).strip().upper()
                    
                    if choice in ['A', 'ABORT', 'Q']:
                        raise click.Abort()
                    elif choice == 'E':
                        break # Proceed to execution
                    elif choice == '1':
                        order['symbol'] = safe_prompt('Trading Symbol', validate_symbol, order['symbol'])
                    elif choice == '2':
                        order['side'] = safe_prompt('Order Side', validate_side, order['side'])
                    elif choice == '3':
                        order['qty'] = safe_prompt('Quantity', validate_quantity, order['qty'])
                    elif choice == '4':
                        old_type = order['type']
                        order['type'] = safe_prompt('Order Type', validate_order_type, order['type'])
                        # If order type changes, ask for relevant price metrics
                        if order['type'] != old_type:
                            if order['type'] == 'LIMIT':
                                order['price'] = safe_prompt('Limit Price', lambda x: validate_price(x, "Price"))
                            elif order['type'] == 'STOP_MARKET':
                                order['stop_price'] = safe_prompt('Stop Price', lambda x: validate_price(x, "Stop Price"))
                    elif choice == '5':
                        if order['type'] == 'LIMIT':
                            order['price'] = safe_prompt('Limit Price', lambda x: validate_price(x, "Price"), order.get('price'))
                        elif order['type'] == 'STOP_MARKET':
                            order['stop_price'] = safe_prompt('Stop Price', lambda x: validate_price(x, "Stop Price"), order.get('stop_price'))
                        else:
                            click.secho("Market orders do not use a price field.", fg="yellow")
                    else:
                        click.secho("Invalid selection.", fg="red")

                # Execution
                if order['type'] == 'LIMIT':
                    response = manager.place_limit_order(order['symbol'], order['side'], order['qty'], order['price'])
                elif order['type'] == 'STOP_MARKET':
                    response = manager.place_stop_market_order(order['symbol'], order['side'], order['qty'], order['stop_price'])
                else:
                    response = manager.place_market_order(order['symbol'], order['side'], order['qty'])
                    
                click.secho(f"\n✅ SUCCESS: Order {response.get('orderId')} Executed!", fg="green", bold=True)

            # ---------------------------------------------------------
            # ACTIONS 2 & 3: VIEW / MODIFY / CANCEL
            # ---------------------------------------------------------
            elif action in ['2', '3']:
                symbol = safe_prompt('Enter Symbol to search open orders (e.g., BTCUSDT)', validate_symbol)
                open_orders = client.get_open_orders(symbol)
                
                if not open_orders:
                    click.secho(f"No active open orders found for {symbol}.", fg="yellow")
                    click.prompt("\nPress Enter to return to the Main Menu...", default="", show_default=False)
                    continue
                    
                click.secho(f"\n--- Active Open Orders for {symbol} ---", fg="cyan", bold=True)
                for idx, o in enumerate(open_orders):
                    click.echo(f"[{idx}] ID: {o['orderId']} | Type: {o['type']} | Side: {o['side']} | Qty: {o['origQty']} | Price: {o.get('price', 'N/A')}")
                    
                choice = safe_prompt('\nEnter bracket number [ ] to select order (or -1 to go back)', lambda x: int(x))
                if choice < 0 or choice >= len(open_orders):
                    click.secho("Returning to Main Menu...", fg="yellow")
                    continue
                    
                selected = open_orders[choice]
                
                if action == '2':
                    if selected['type'] != 'LIMIT':
                        click.secho("Binance only allows modifying active LIMIT orders.", fg="red", bold=True)
                        click.prompt("\nPress Enter to return to the Main Menu...", default="", show_default=False)
                        continue
                    new_price = safe_prompt('Enter NEW Limit Price', lambda x: validate_price(x, "Price"))
                    response = manager.modify_limit_order(symbol, selected['side'], float(selected['origQty']), new_price, selected['orderId'])
                    click.secho(f"\n✅ SUCCESS: Order {response.get('orderId')} Modified!", fg="green", bold=True)
                    
                elif action == '3':
                    response = manager.cancel_specific_order(symbol, selected['orderId'])
                    click.secho(f"\n✅ SUCCESS: Order {response.get('orderId')} Cancelled!", fg="green", bold=True)

            # ---------------------------------------------------------
            # ACTION 4: GRID / BASKET (WITH REVIEW/EDIT MENU)
            # ---------------------------------------------------------
            elif action == '4':
                click.secho("\n--- GRID ORDER SETUP (Type 'abort' to cancel) ---", fg="cyan", bold=True)
                grid = {
                    'symbol': safe_prompt('Trading Symbol (e.g., BTCUSDT)', validate_symbol),
                    'side': safe_prompt('Order Side (BUY/SELL)', validate_side),
                    'qty': safe_prompt('Total Basket Quantity', validate_quantity),
                    'price': safe_prompt('Starting Price', lambda x: validate_price(x, "Price")),
                    'levels': safe_prompt('How many orders in the basket?', validate_levels),
                    'step': safe_prompt('Price difference between each order', lambda x: validate_price(x, "Step"))
                }
                
                # Review & Edit Loop
                while True:
                    click.secho("\n--- Grid Summary Review ---", fg="yellow", bold=True)
                    click.echo(f"1. Symbol:       {grid['symbol']}")
                    click.echo(f"2. Side:         {grid['side']}")
                    click.echo(f"3. Total Qty:    {grid['qty']}")
                    click.echo(f"4. Start Price:  {grid['price']}")
                    click.echo(f"5. Levels:       {grid['levels']}")
                    click.echo(f"6. Price Step:   {grid['step']}")
                    
                    click.secho("\nOptions: [E] Execute | [A] Abort | [#] Number to Edit Field", fg="cyan")
                    choice = click.prompt("Select an option", type=str).strip().upper()
                    
                    if choice in ['A', 'ABORT', 'Q']:
                        raise click.Abort()
                    elif choice == 'E':
                        break
                    elif choice == '1': grid['symbol'] = safe_prompt('Trading Symbol', validate_symbol, grid['symbol'])
                    elif choice == '2': grid['side'] = safe_prompt('Order Side', validate_side, grid['side'])
                    elif choice == '3': grid['qty'] = safe_prompt('Total Qty', validate_quantity, grid['qty'])
                    elif choice == '4': grid['price'] = safe_prompt('Start Price', lambda x: validate_price(x, "Price"), grid['price'])
                    elif choice == '5': grid['levels'] = safe_prompt('Levels', validate_levels, grid['levels'])
                    elif choice == '6': grid['step'] = safe_prompt('Price Step', lambda x: validate_price(x, "Step"), grid['step'])
                    else: click.secho("Invalid selection.", fg="red")

                responses = manager.place_grid_basket_order(grid['symbol'], grid['side'], grid['qty'], grid['price'], grid['levels'], grid['step'])
                click.secho(f"\n✅ SUCCESS: {len(responses)} Basket Orders Placed!", fg="green", bold=True)

            click.prompt("\nPress Enter to return to Main Menu...", default="", show_default=False)

        except InputValidationError as e:
            click.secho(f"\n❌ VALIDATION ERROR: {e}", fg="red", bold=True)
            click.prompt("\nPress Enter to return to Main Menu...", default="", show_default=False)
            
        except (click.Abort, KeyboardInterrupt):
            # Cleanly intercepts Ctrl+C or text-aborts and resets immediately
            click.secho("\n⚠️ Action reset by user. Returning to Main Menu...", fg="yellow", bold=True)
            time.sleep(1) # Brief pause so you can read the message before it clears
            continue 
            
        except Exception as e:
            error_msg = str(e) if str(e) else repr(e)
            click.secho(f"\n❌ EXECUTION FAILED: {error_msg}", fg="red", bold=True)
            click.secho("Check logs/trading_bot.log for complete structural details.", fg="yellow")
            click.prompt("\nPress Enter to return to Main Menu...", default="", show_default=False)

@click.command()
def main():
    try:
        run_bot()
    except (KeyboardInterrupt, click.Abort):
        click.secho("\nBot terminated process gracefully. Goodbye!", fg="yellow", bold=True)

if __name__ == '__main__':
    main()