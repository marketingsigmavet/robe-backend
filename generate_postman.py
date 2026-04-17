import os
import yaml

base_dir = r"E:\Robe\robe-backend\postman\collections\RoBe Backend API"

folders = [
    "14 - Admin Product Brands",
    "15 - Admin Product Categories",
]

for f in folders:
    os.makedirs(os.path.join(base_dir, f), exist_ok=True)

# Helper function to write yaml
def write_req(folder, name, method, url, body_content=None):
    data = {
        "$kind": "http-request",
        "name": name,
        "method": method,
        "url": url,
        "headers": [
            {"key": "Authorization", "value": "Bearer {{access_token}}"}
        ]
    }
    
    if body_content:
        data["headers"].append({"key": "Content-Type", "value": "application/json"})
        data["body"] = {
            "type": "json",
            "content": body_content
        }
        
    file_path = os.path.join(base_dir, folder, f"{name}.request.yaml")
    with open(file_path, "w") as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)


# 14 - Admin Product Brands
write_req("14 - Admin Product Brands", "List Brands", "GET", "{{base_url}}/admin/product-brands")
write_req("14 - Admin Product Brands", "Get Brand", "GET", "{{base_url}}/admin/product-brands/{{brand_id}}")
write_req("14 - Admin Product Brands", "Create Brand", "POST", "{{base_url}}/admin/product-brands", "{\n  \"brand_name\": \"Acme Pet Corp\",\n  \"description\": \"Quality products\",\n  \"website_url\": \"https://acme.com\"\n}")
write_req("14 - Admin Product Brands", "Update Brand", "PATCH", "{{base_url}}/admin/product-brands/{{brand_id}}", "{\n  \"description\": \"Updated Brand Info\"\n}")
write_req("14 - Admin Product Brands", "Delete Brand", "DELETE", "{{base_url}}/admin/product-brands/{{brand_id}}")

# 15 - Admin Product Categories
write_req("15 - Admin Product Categories", "List Categories", "GET", "{{base_url}}/admin/product-categories")
write_req("15 - Admin Product Categories", "Get Category", "GET", "{{base_url}}/admin/product-categories/{{category_id}}")
write_req("15 - Admin Product Categories", "Create Category", "POST", "{{base_url}}/admin/product-categories", "{\n  \"category_name\": \"Dry Food\",\n  \"description\": \"Kibble and dry variants\"\n}")
write_req("15 - Admin Product Categories", "Update Category", "PATCH", "{{base_url}}/admin/product-categories/{{category_id}}", "{\n  \"description\": \"Updated Category Info\"\n}")
write_req("15 - Admin Product Categories", "Delete Category", "DELETE", "{{base_url}}/admin/product-categories/{{category_id}}")
