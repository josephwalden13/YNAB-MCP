from Account import Account
from AppContext import AppContext
from Budget import Budget
from Category import Category
from contextlib import asynccontextmanager
from mcp.server.fastmcp import FastMCP
from Month import Month
from Payee import Payee
from Transaction import Transaction
from YNABClient import YNABClient


@asynccontextmanager
async def app_lifespan(server: FastMCP):
    ynab = YNABClient()
    try:
        yield AppContext(ynab=ynab)
    finally:
        pass


# Initialize FastMCP server
mcp = FastMCP(
    "ynab",
    lifespan=app_lifespan,
)

# Register all tools
Transaction.RegisterTools(mcp)
Budget.RegisterTools(mcp)
Category.RegisterTools(mcp)
Month.RegisterTools(mcp)
Account.RegisterTools(mcp)
Payee.RegisterTools(mcp)

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
