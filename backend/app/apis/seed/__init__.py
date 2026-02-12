from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.auth import AuthorizedUser
import json
import databutton as db
import uuid
from datetime import datetime
from firebase_admin import firestore
from app.apis.firebase_admin import firestore_db

router = APIRouter()

class SeedResponse(BaseModel):
    success: bool
    message: str

@router.post("/seed-product-catalog")
async def seed_product_catalog(user: AuthorizedUser) -> SeedResponse:
    """Seed the product catalog with initial data. This should only be run once."""
    
    # Check if data already exists in storage
    try:
        if db.storage.json.get("product_catalog_seeded", default=None):
            return SeedResponse(success=False, message="Product catalog has already been seeded.")
    except:
        pass
    
    # Define categories
    categories = [
        {
            "id": "cbd-oils",
            "name": "CBD Oils",
            "description": "High-quality CBD oils in various strengths and formulations.",
            "parent_id": None,
            "image_url": "https://images.unsplash.com/photo-1617082552469-f03be81366b2?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "order": 1,
            "active": True
        },
        {
            "id": "cbd-capsules",
            "name": "CBD Capsules",
            "description": "Easy-to-take CBD capsules with precise dosing.",
            "parent_id": None,
            "image_url": "https://images.unsplash.com/photo-1584362917165-526a968579e8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "order": 2,
            "active": True
        },
        {
            "id": "cbg-products",
            "name": "CBG Products",
            "description": "CBG-rich products for enhanced wellness benefits.",
            "parent_id": None,
            "image_url": "https://images.unsplash.com/photo-1590564310418-66304f55a2c2?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "order": 3,
            "active": True
        },
        {
            "id": "hemp-flower",
            "name": "Hemp Flower",
            "description": "Premium, low-THC hemp flower for personal use.",
            "parent_id": None,
            "image_url": "https://images.unsplash.com/photo-1603909223429-69bb7101f94e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "order": 4,
            "active": True
        },
        {
            "id": "topicals",
            "name": "Topicals",
            "description": "CBD-infused creams and balms for localized relief.",
            "parent_id": None,
            "image_url": "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
            "order": 5,
            "active": True
        }
    ]
    
    # Define lab results
    lab_results = [
        {
            "id": "lab-result-001",
            "date": "2025-01-15",
            "lab_name": "Australian Cannabis Testing",
            "document_url": "https://static.databutton.com/public/abfc4236-481d-4bd9-bfe1-7a0124980081/lab-result-001.pdf",
            "verified": True
        },
        {
            "id": "lab-result-002",
            "date": "2025-02-10",
            "lab_name": "Australian Cannabis Testing",
            "document_url": "https://static.databutton.com/public/abfc4236-481d-4bd9-bfe1-7a0124980081/lab-result-002.pdf",
            "verified": True
        },
        {
            "id": "lab-result-003",
            "date": "2025-03-05",
            "lab_name": "Cannabinoid Analysis Labs",
            "document_url": "https://static.databutton.com/public/abfc4236-481d-4bd9-bfe1-7a0124980081/lab-result-003.pdf",
            "verified": True
        },
        {
            "id": "lab-result-004",
            "date": "2025-03-22",
            "lab_name": "Cannabinoid Analysis Labs",
            "document_url": "https://static.databutton.com/public/abfc4236-481d-4bd9-bfe1-7a0124980081/lab-result-004.pdf",
            "verified": True
        }
    ]
    
    # Define products
    products = [
        # CBD Oils
        {
            "sku": "CBD-OIL-1000",
            "name": "Premium CBD Oil 1000mg",
            "description": "Our high-quality CBD oil contains 1000mg of premium CBD extract in a base of organic MCT oil. This full-spectrum formula preserves all the beneficial compounds found in hemp for maximum effectiveness.",
            "category_id": "cbd-oils",
            "category_name": "CBD Oils",
            "image_urls": [
                "https://images.unsplash.com/photo-1595229207190-f62a24bf976b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80",
                "https://images.unsplash.com/photo-1559099845-3cec8fea2811?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 1000,
                    "unit": "mg"
                },
                {
                    "name": "THC",
                    "amount": 0.2,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-001"],
            "tga_approved": True,
            "artg_number": "123456",
            "price": 89.95,
            "in_stock": True,
            "stock_quantity": 50,
            "requires_prescription": False,
            "usage_instructions": "Take 1 dropper (1ml) under the tongue once or twice daily. Hold for 60 seconds before swallowing. Start with a lower dose and gradually increase as needed.",
            "featured": True,
            "related_products": ["CBD-OIL-2000", "CBD-OIL-500"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "CBD-OIL-2000",
            "name": "Premium CBD Oil 2000mg",
            "description": "Our highest strength CBD oil contains 2000mg of premium CBD extract in a base of organic MCT oil. This full-spectrum formula is perfect for those seeking a higher dose of CBD for their wellness routine.",
            "category_id": "cbd-oils",
            "category_name": "CBD Oils",
            "image_urls": [
                "https://images.unsplash.com/photo-1595229207190-f62a24bf976b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 2000,
                    "unit": "mg"
                },
                {
                    "name": "THC",
                    "amount": 0.2,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-001"],
            "tga_approved": True,
            "artg_number": "123457",
            "price": 149.95,
            "in_stock": True,
            "stock_quantity": 35,
            "requires_prescription": False,
            "usage_instructions": "Take 1 dropper (1ml) under the tongue once daily. Hold for 60 seconds before swallowing. Start with a lower dose and gradually increase as needed.",
            "featured": False,
            "related_products": ["CBD-OIL-1000", "CBD-OIL-500"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "CBD-OIL-500",
            "name": "Premium CBD Oil 500mg",
            "description": "Our entry-level CBD oil contains 500mg of premium CBD extract in a base of organic MCT oil. Perfect for those new to CBD or those who prefer a lower dose in their daily routine.",
            "category_id": "cbd-oils",
            "category_name": "CBD Oils",
            "image_urls": [
                "https://images.unsplash.com/photo-1559099845-3cec8fea2811?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 500,
                    "unit": "mg"
                },
                {
                    "name": "THC",
                    "amount": 0.1,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-002"],
            "tga_approved": True,
            "artg_number": "123458",
            "price": 59.95,
            "in_stock": True,
            "stock_quantity": 75,
            "requires_prescription": False,
            "usage_instructions": "Take 1 dropper (1ml) under the tongue once or twice daily. Hold for 60 seconds before swallowing.",
            "featured": True,
            "related_products": ["CBD-OIL-1000"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        
        # CBD Capsules
        {
            "sku": "CBD-CAP-300",
            "name": "CBD Capsules 300mg (30 count)",
            "description": "Our CBD capsules offer a convenient way to incorporate CBD into your daily routine. Each capsule contains 10mg of premium CBD in an easy-to-swallow vegetarian capsule.",
            "category_id": "cbd-capsules",
            "category_name": "CBD Capsules",
            "image_urls": [
                "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 10,
                    "unit": "mg/capsule"
                },
                {
                    "name": "Total CBD",
                    "amount": 300,
                    "unit": "mg/bottle"
                }
            ],
            "lab_results": ["lab-result-002"],
            "tga_approved": True,
            "artg_number": "123459",
            "price": 49.95,
            "in_stock": True,
            "stock_quantity": 100,
            "requires_prescription": False,
            "usage_instructions": "Take 1-2 capsules daily with water, preferably with food.",
            "featured": False,
            "related_products": ["CBD-CAP-600"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "CBD-CAP-600",
            "name": "CBD Capsules 600mg (60 count)",
            "description": "Our higher-dose CBD capsules provide a convenient way to incorporate CBD into your daily routine. Each capsule contains 10mg of premium CBD in an easy-to-swallow vegetarian capsule.",
            "category_id": "cbd-capsules",
            "category_name": "CBD Capsules",
            "image_urls": [
                "https://images.unsplash.com/photo-1584362917165-526a968579e8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 10,
                    "unit": "mg/capsule"
                },
                {
                    "name": "Total CBD",
                    "amount": 600,
                    "unit": "mg/bottle"
                }
            ],
            "lab_results": ["lab-result-002"],
            "tga_approved": True,
            "artg_number": "123460",
            "price": 89.95,
            "in_stock": True,
            "stock_quantity": 80,
            "requires_prescription": False,
            "usage_instructions": "Take 1-2 capsules daily with water, preferably with food.",
            "featured": True,
            "related_products": ["CBD-CAP-300"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "CBD-CAP-900",
            "name": "CBD Capsules 900mg (30 count)",
            "description": "Our highest strength CBD capsules for those requiring a more potent dose. Each capsule contains 30mg of premium CBD in an easy-to-swallow vegetarian capsule.",
            "category_id": "cbd-capsules",
            "category_name": "CBD Capsules",
            "image_urls": [
                "https://images.unsplash.com/photo-1584441395251-2c8501faffac?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 30,
                    "unit": "mg/capsule"
                },
                {
                    "name": "Total CBD",
                    "amount": 900,
                    "unit": "mg/bottle"
                }
            ],
            "lab_results": ["lab-result-002"],
            "tga_approved": True,
            "artg_number": "123461",
            "price": 119.95,
            "in_stock": True,
            "stock_quantity": 60,
            "requires_prescription": False,
            "usage_instructions": "Take 1 capsule daily with water, preferably with food. Due to the higher potency, start with one capsule and adjust as needed.",
            "featured": False,
            "related_products": ["CBD-CAP-300", "CBD-CAP-600"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        
        # CBG Products
        {
            "sku": "CBG-OIL-500",
            "name": "CBG Oil 500mg",
            "description": "Our CBG oil harnesses the power of cannabigerol, a non-intoxicating cannabinoid known for its unique wellness benefits. This formula contains 500mg of CBG in a base of organic MCT oil.",
            "category_id": "cbg-products",
            "category_name": "CBG Products",
            "image_urls": [
                "https://images.unsplash.com/photo-1609686657209-7b0a3ff903d7?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBG",
                    "amount": 500,
                    "unit": "mg"
                },
                {
                    "name": "CBD",
                    "amount": 50,
                    "unit": "mg"
                },
                {
                    "name": "THC",
                    "amount": 0.1,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-003"],
            "tga_approved": True,
            "artg_number": "123462",
            "price": 79.95,
            "in_stock": True,
            "stock_quantity": 40,
            "requires_prescription": False,
            "usage_instructions": "Take 1 dropper (1ml) under the tongue once daily. Hold for 60 seconds before swallowing.",
            "featured": True,
            "related_products": ["CBG-OIL-1000", "CBD-OIL-1000"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "CBG-OIL-1000",
            "name": "CBG Oil 1000mg",
            "description": "Our higher-strength CBG oil delivers 1000mg of cannabigerol, a non-intoxicating cannabinoid with unique wellness properties. Formulated in a base of organic MCT oil for optimal absorption.",
            "category_id": "cbg-products",
            "category_name": "CBG Products",
            "image_urls": [
                "https://images.unsplash.com/photo-1616876195047-522bd83c9cb2?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBG",
                    "amount": 1000,
                    "unit": "mg"
                },
                {
                    "name": "CBD",
                    "amount": 100,
                    "unit": "mg"
                },
                {
                    "name": "THC",
                    "amount": 0.1,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-003"],
            "tga_approved": True,
            "artg_number": "123463",
            "price": 129.95,
            "in_stock": True,
            "stock_quantity": 30,
            "requires_prescription": False,
            "usage_instructions": "Take 1 dropper (1ml) under the tongue once daily. Hold for 60 seconds before swallowing. Start with a smaller amount and gradually increase.",
            "featured": False,
            "related_products": ["CBG-OIL-500", "CBD-OIL-2000"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "CBG-ISO-1000",
            "name": "CBG Isolate 1000mg",
            "description": "Our pure CBG isolate powder is 99%+ CBG with no other cannabinoids. Perfect for creating your own CBG products or for those seeking the benefits of CBG without any other compounds.",
            "category_id": "cbg-products",
            "category_name": "CBG Products",
            "image_urls": [
                "https://images.unsplash.com/photo-1616876480260-5e3cc67ea445?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBG",
                    "amount": 99.5,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-003", "lab-result-004"],
            "tga_approved": True,
            "artg_number": "123464",
            "price": 99.95,
            "in_stock": True,
            "stock_quantity": 25,
            "requires_prescription": False,
            "usage_instructions": "Can be used to make your own CBG preparations. Suggested use is 10-50mg per day, depending on individual needs.",
            "featured": False,
            "related_products": ["CBG-OIL-500", "CBG-OIL-1000"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        
        # Hemp Flower
        {
            "sku": "HEMP-FLOW-BBS",
            "name": "Blueberry Strain Hemp Flower",
            "description": "Our Blueberry strain hemp flower has a sweet berry aroma and relaxing effects. Contains less than 0.3% THC and rich in CBD, perfect for those seeking the benefits of hemp without the high.",
            "category_id": "hemp-flower",
            "category_name": "Hemp Flower",
            "image_urls": [
                "https://images.unsplash.com/photo-1603909223429-69bb7101f94e?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 15.5,
                    "unit": "%"
                },
                {
                    "name": "CBG",
                    "amount": 0.8,
                    "unit": "%"
                },
                {
                    "name": "THC",
                    "amount": 0.2,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-004"],
            "tga_approved": True,
            "artg_number": "123465",
            "price": 49.95,
            "in_stock": True,
            "stock_quantity": 50,
            "requires_prescription": False,
            "usage_instructions": "For aromatic and personal use only. Store in a cool, dry place away from direct sunlight.",
            "featured": True,
            "related_products": ["HEMP-FLOW-LC", "HEMP-FLOW-SC"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "HEMP-FLOW-LC",
            "name": "Lemon Cherry Hemp Flower",
            "description": "Our Lemon Cherry hemp flower has a citrusy aroma with cherry undertones. Contains less than 0.3% THC and high levels of CBD and terpenes for a pleasant experience.",
            "category_id": "hemp-flower",
            "category_name": "Hemp Flower",
            "image_urls": [
                "https://images.unsplash.com/photo-1603913996638-c681ca391c0a?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 18.2,
                    "unit": "%"
                },
                {
                    "name": "CBG",
                    "amount": 1.2,
                    "unit": "%"
                },
                {
                    "name": "THC",
                    "amount": 0.25,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-004"],
            "tga_approved": True,
            "artg_number": "123466",
            "price": 54.95,
            "in_stock": True,
            "stock_quantity": 45,
            "requires_prescription": False,
            "usage_instructions": "For aromatic and personal use only. Store in a cool, dry place away from direct sunlight.",
            "featured": False,
            "related_products": ["HEMP-FLOW-BBS", "HEMP-FLOW-SC"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "HEMP-FLOW-SC",
            "name": "Sour CBD Hemp Flower",
            "description": "Our Sour CBD hemp flower offers a tangy, diesel-like aroma and is rich in terpenes. Contains less than 0.3% THC and high levels of CBD for a balanced experience.",
            "category_id": "hemp-flower",
            "category_name": "Hemp Flower",
            "image_urls": [
                "https://images.unsplash.com/photo-1603916071968-c30de4a05ca0?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 20.1,
                    "unit": "%"
                },
                {
                    "name": "CBG",
                    "amount": 0.5,
                    "unit": "%"
                },
                {
                    "name": "THC",
                    "amount": 0.28,
                    "unit": "%"
                }
            ],
            "lab_results": ["lab-result-004"],
            "tga_approved": True,
            "artg_number": "123467",
            "price": 59.95,
            "in_stock": True,
            "stock_quantity": 35,
            "requires_prescription": False,
            "usage_instructions": "For aromatic and personal use only. Store in a cool, dry place away from direct sunlight.",
            "featured": False,
            "related_products": ["HEMP-FLOW-BBS", "HEMP-FLOW-LC"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        
        # Topicals
        {
            "sku": "CBD-CREAM-500",
            "name": "CBD Cooling Relief Cream 500mg",
            "description": "Our CBD cooling relief cream combines 500mg of premium CBD with menthol and arnica for localized relief. Perfect for sore muscles and joints after physical activity.",
            "category_id": "topicals",
            "category_name": "Topicals",
            "image_urls": [
                "https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 500,
                    "unit": "mg"
                }
            ],
            "lab_results": ["lab-result-002"],
            "tga_approved": True,
            "artg_number": "123468",
            "price": 49.95,
            "in_stock": True,
            "stock_quantity": 75,
            "requires_prescription": False,
            "usage_instructions": "Apply a small amount to the affected area and massage gently. Repeat up to 3-4 times daily as needed. For external use only.",
            "featured": True,
            "related_products": ["CBD-BALM-250"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "CBD-BALM-250",
            "name": "CBD Soothing Balm 250mg",
            "description": "Our CBD soothing balm combines 250mg of premium CBD with essential oils and shea butter for deep moisturization and relief. Ideal for dry, irritated skin and localized discomfort.",
            "category_id": "topicals",
            "category_name": "Topicals",
            "image_urls": [
                "https://images.unsplash.com/photo-1608248544299-781e4a351291?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 250,
                    "unit": "mg"
                }
            ],
            "lab_results": ["lab-result-002"],
            "tga_approved": True,
            "artg_number": "123469",
            "price": 39.95,
            "in_stock": True,
            "stock_quantity": 60,
            "requires_prescription": False,
            "usage_instructions": "Apply a small amount to clean, dry skin and massage gently until absorbed. Use as needed throughout the day. For external use only.",
            "featured": False,
            "related_products": ["CBD-CREAM-500"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "sku": "CBD-ROLL-150",
            "name": "CBD Roll-On Relief 150mg",
            "description": "Our CBD roll-on provides convenient, targeted relief with 150mg of CBD plus cooling menthol and warming camphor. The roll-on applicator makes it easy to apply without mess.",
            "category_id": "topicals",
            "category_name": "Topicals",
            "image_urls": [
                "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80"
            ],
            "cannabinoids": [
                {
                    "name": "CBD",
                    "amount": 150,
                    "unit": "mg"
                }
            ],
            "lab_results": ["lab-result-002"],
            "tga_approved": True,
            "artg_number": "123470",
            "price": 29.95,
            "in_stock": True,
            "stock_quantity": 90,
            "requires_prescription": False,
            "usage_instructions": "Roll directly onto affected areas up to 4 times daily. Do not apply to broken skin or mucous membranes. For external use only.",
            "featured": False,
            "related_products": ["CBD-CREAM-500", "CBD-BALM-250"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    # Store the data in Databutton storage for future reference or restoration
    db.storage.json.put("product_categories", categories)
    db.storage.json.put("product_lab_results", lab_results)
    db.storage.json.put("product_catalog", products)

    try:
        # Add data directly to Firestore
        # Add categories
        for category in categories:
            firestore_db.collection('categories').document(category['id']).set(category)
        
        # Add lab results
        for lab_result in lab_results:
            firestore_db.collection('lab_results').document(lab_result['id']).set(lab_result)
        
        # Add products
        for product in products:
            firestore_db.collection('products').document(product['sku']).set(product)
        
        # Mark as seeded to prevent duplicate seeding
        db.storage.json.put("product_catalog_seeded", {"seeded": True, "timestamp": datetime.now().isoformat()})
        
        return SeedResponse(success=True, message="Product catalog successfully seeded with categories, lab results, and products.")
    except Exception as e:
        return SeedResponse(success=False, message=f"Error seeding product catalog: {str(e)}")
