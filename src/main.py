from mcp.server.fastmcp import FastMCP
from tools import (
    register_user_tools,
    register_budget_tools,
    register_account_tools,
    register_payee_tools,
    register_month_tools,
    register_category_tools,
    register_transaction_tools,
)

# Initialize FastMCP server
mcp = FastMCP(
    "ynab",
    instructions="""You are a virtual accountant connected to the YNAB API. 
    You can help users manage their budgets, accounts, transactions, and categories.
    Unless explicitly told otherwise, always use the 'last-used' budget.""",
)

# Register all tools
register_user_tools(mcp)
register_budget_tools(mcp)
register_account_tools(mcp)
register_payee_tools(mcp)
register_month_tools(mcp)
register_category_tools(mcp)
register_transaction_tools(mcp)


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="stdio")
