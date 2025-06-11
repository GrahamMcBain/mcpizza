import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// Pizza ordering state
interface PizzaOrder {
	items: Array<{
		item_code: string;
		name: string;
		quantity: number;
		price: number;
		options?: any;
	}>;
	store?: any;
	customer?: any;
	total?: number;
}

class PizzaOrderManager {
	private order: PizzaOrder = { items: [] };
	private selectedStore: any = null;

	// Mock data for demo purposes (replace with real API calls)
	private mockStores = [
		{ id: "10001", name: "Domino's - Manhattan", address: "123 Broadway, New York, NY 10001" },
		{ id: "95608", name: "Domino's - Auburn", address: "456 Main St, Auburn, CA 95608" }
	];

	private mockMenuItems = [
		{ code: "M_PEPPERONI", name: "Medium Pepperoni Pizza", price: 12.99, category: "pizza" },
		{ code: "L_MARGHERITA", name: "Large Margherita Pizza", price: 15.99, category: "pizza" },
		{ code: "WINGS_BBQ", name: "BBQ Wings (8pc)", price: 8.99, category: "wings" },
		{ code: "PASTA_ALFREDO", name: "Chicken Alfredo Pasta", price: 10.99, category: "pasta" }
	];

	findStore(address: string) {
		// Mock store finding based on address
		const store = this.mockStores.find(s => s.id === address || s.address.includes(address));
		if (store) {
			this.selectedStore = store;
			return { success: true, store: store, message: `Found store: ${store.name}` };
		}
		return { success: false, error: "No store found for the given address" };
	}

	getMenuCategories() {
		if (!this.selectedStore) {
			return { error: "Please select a store first using find_dominos_store" };
		}
		return {
			success: true,
			categories: ["pizza", "wings", "pasta", "sides", "drinks"],
			store: this.selectedStore.name
		};
	}

	searchMenu(query: string) {
		if (!this.selectedStore) {
			return { error: "Please select a store first using find_dominos_store" };
		}
		
		const results = this.mockMenuItems.filter(item => 
			item.name.toLowerCase().includes(query.toLowerCase()) ||
			item.category.toLowerCase().includes(query.toLowerCase())
		);

		return {
			success: true,
			query: query,
			items: results,
			count: results.length
		};
	}

	addToOrder(itemCode: string, quantity: number = 1, options: any = {}) {
		const item = this.mockMenuItems.find(i => i.code === itemCode);
		if (!item) {
			return { error: `Item with code ${itemCode} not found` };
		}

		this.order.items.push({
			item_code: itemCode,
			name: item.name,
			quantity: quantity,
			price: item.price,
			options: options
		});

		return {
			success: true,
			message: `Added ${quantity}x ${item.name} to order`,
			order_items: this.order.items.length
		};
	}

	viewOrder() {
		return {
			success: true,
			order: this.order,
			total_items: this.order.items.length,
			estimated_total: this.order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0)
		};
	}

	setCustomerInfo(info: any) {
		this.order.customer = info;
		return {
			success: true,
			message: "Customer information saved",
			customer: info
		};
	}

	calculateTotal() {
		const subtotal = this.order.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
		const tax = subtotal * 0.08; // 8% tax
		const deliveryFee = 2.99;
		const total = subtotal + tax + deliveryFee;

		this.order.total = total;

		return {
			success: true,
			breakdown: {
				subtotal: Math.round(subtotal * 100) / 100,
				tax: Math.round(tax * 100) / 100,
				delivery_fee: deliveryFee,
				total: Math.round(total * 100) / 100
			}
		};
	}

	prepareOrderPreview() {
		if (this.order.items.length === 0) {
			return { error: "No items in order" };
		}

		return {
			success: true,
			message: "Order prepared for preview (safe mode - no actual order placed)",
			preview: {
				store: this.selectedStore,
				customer: this.order.customer,
				items: this.order.items,
				total: this.order.total || this.calculateTotal().breakdown.total
			},
			warning: "Real order placement is disabled for safety"
		};
	}
}

// Define our MCP agent with pizza ordering tools
export class MyMCP extends McpAgent {
	server = new McpServer({
		name: "MCPizza - Domino's Pizza Ordering",
		version: "1.0.0",
	});

	private pizzaManager = new PizzaOrderManager();

	async init() {
		// Find Domino's store tool
		this.server.tool(
			"find_dominos_store",
			{ 
				address: z.string().describe("Full address or zip code to search near")
			},
			async ({ address }) => {
				const result = this.pizzaManager.findStore(address);
				return {
					content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
				};
			}
		);

		// Get store menu categories
		this.server.tool(
			"get_store_menu_categories",
			{},
			async () => {
				const result = this.pizzaManager.getMenuCategories();
				return {
					content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
				};
			}
		);

		// Search menu tool
		this.server.tool(
			"search_menu",
			{
				query: z.string().describe("Search term (e.g., 'pepperoni pizza', 'wings', 'pasta')")
			},
			async ({ query }) => {
				const result = this.pizzaManager.searchMenu(query);
				return {
					content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
				};
			}
		);

		// Add to order tool
		this.server.tool(
			"add_to_order",
			{
				item_code: z.string().describe("Product code from menu search"),
				quantity: z.number().default(1).describe("Number of items to add"),
				options: z.any().optional().describe("Item customization options")
			},
			async ({ item_code, quantity, options }) => {
				const result = this.pizzaManager.addToOrder(item_code, quantity, options);
				return {
					content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
				};
			}
		);

		// View order tool
		this.server.tool(
			"view_order",
			{},
			async () => {
				const result = this.pizzaManager.viewOrder();
				return {
					content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
				};
			}
		);

		// Set customer info tool
		this.server.tool(
			"set_customer_info",
			{
				first_name: z.string(),
				last_name: z.string(),
				email: z.string(),
				phone: z.string(),
				address: z.object({
					street: z.string(),
					city: z.string(),
					region: z.string(),
					zip: z.string()
				})
			},
			async (customerInfo) => {
				const result = this.pizzaManager.setCustomerInfo(customerInfo);
				return {
					content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
				};
			}
		);

		// Calculate order total tool
		this.server.tool(
			"calculate_order_total",
			{},
			async () => {
				const result = this.pizzaManager.calculateTotal();
				return {
					content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
				};
			}
		);

		// Prepare order preview tool
		this.server.tool(
			"prepare_order",
			{},
			async () => {
				const result = this.pizzaManager.prepareOrderPreview();
				return {
					content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
				};
			}
		);
	}
}

export default {
	fetch(request: Request, env: Env, ctx: ExecutionContext) {
		const url = new URL(request.url);

		if (url.pathname === "/sse" || url.pathname === "/sse/message") {
			return MyMCP.serveSSE("/sse").fetch(request, env, ctx);
		}

		if (url.pathname === "/mcp") {
			return MyMCP.serve("/mcp").fetch(request, env, ctx);
		}

		return new Response("Not found", { status: 404 });
	},
};
