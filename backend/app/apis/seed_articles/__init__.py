from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from firebase_admin import firestore
import firebase_admin
from firebase_admin import credentials
import databutton as db
import json
from datetime import datetime, timedelta
import random

# Initialize Firebase Admin SDK if not already initialized
try:
    app = firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(json.loads(db.secrets.get("FIREBASE_SERVICE_ACCOUNT")))
    app = firebase_admin.initialize_app(cred)

router = APIRouter()
db_client = firestore.client()

class SeedArticlesRequest(BaseModel):
    force_reset: bool = False

class SeedArticlesResponse(BaseModel):
    message: str
    count: int
    categories_count: int
    tags_count: int
    authors_count: int

@router.post("/seed-articles")
def seed_articles(request: SeedArticlesRequest) -> SeedArticlesResponse:
    """
    Seeds the Firestore database with sample educational content about cannabinoids.
    If force_reset is True, it will delete existing documents before seeding.
    """
    
    # Check if we already have articles
    articles_ref = db_client.collection('articles')
    existing_articles = list(articles_ref.limit(1).stream())
    
    if existing_articles and not request.force_reset:
        return SeedArticlesResponse(
            message="Articles already exist. Use force_reset=True to reseed.",
            count=len(list(articles_ref.stream())),
            categories_count=len(list(db_client.collection('categories').stream())),
            tags_count=len(list(db_client.collection('tags').stream())),
            authors_count=len(list(db_client.collection('authors').stream()))
        )
    
    # If force_reset is True, delete existing data
    if request.force_reset:
        # Delete all articles
        for doc in articles_ref.stream():
            doc.reference.delete()
        
        # Delete all categories
        for doc in db_client.collection('categories').stream():
            doc.reference.delete()
        
        # Delete all tags
        for doc in db_client.collection('tags').stream():
            doc.reference.delete()
        
        # Delete all authors (keep any that might be real users)
        for doc in db_client.collection('authors').stream():
            # Only delete sample authors we've created
            if doc.to_dict().get('is_sample', False):
                doc.reference.delete()
    
    # Create authors
    authors = [
        {
            "name": "Dr. Emily Chen",
            "bio": "Dr. Emily Chen is a pharmacologist specializing in cannabinoid research with over 15 years of experience studying their effects on the endocannabinoid system. She holds a Ph.D. in Pharmacology from UC San Francisco and has published numerous peer-reviewed articles on cannabinoid therapies.",
            "avatar": "https://images.unsplash.com/photo-1551836022-deb4988cc6c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80",
            "is_sample": True
        },
        {
            "name": "Michael Thompson",
            "bio": "Michael Thompson is a certified holistic health practitioner and cannabis educator. With 10+ years in the wellness industry, he specializes in integrating cannabinoids into comprehensive wellness programs. He holds certifications in nutritional therapy and cannabinoid science.",
            "avatar": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80",
            "is_sample": True
        },
        {
            "name": "Dr. Sarah Williams",
            "bio": "Dr. Sarah Williams is a neurologist with a special interest in how cannabinoids interact with the nervous system. Her research focuses on applications for pain management and neurological disorders. She earned her medical degree from Johns Hopkins University and has been researching cannabinoids for over 8 years.",
            "avatar": "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?ixlib=rb-4.0.3&auto=format&fit=crop&w=200&q=80",
            "is_sample": True
        }
    ]
    
    # Add authors to Firestore
    authors_ref = db_client.collection('authors')
    author_refs = []
    for author in authors:
        # Check if author already exists
        existing_author = list(authors_ref.where("name", "==", author["name"]).limit(1).stream())
        if existing_author:
            author_refs.append(existing_author[0].id)
        else:
            doc_ref = authors_ref.add(author)[1]
            author_refs.append(doc_ref.id)
    
    # Create categories
    categories = [
        {
            "id": "cbd-explained",
            "name": "CBD Explained",
            "description": "Everything you need to know about CBD, from basic explanations to advanced science."
        },
        {
            "id": "cbg-explained",
            "name": "CBG Explained",
            "description": "Learn about cannabigerol (CBG), its potential benefits, and how it differs from other cannabinoids."
        },
        {
            "id": "science",
            "name": "Cannabinoid Science",
            "description": "Scientific insights into how cannabinoids work in the body and their therapeutic potential."
        },
        {
            "id": "wellness",
            "name": "Wellness & Lifestyle",
            "description": "How to incorporate cannabinoids into your wellness routine and lifestyle."
        },
        {
            "id": "guides",
            "name": "How-To Guides",
            "description": "Practical guides for understanding, selecting, and using cannabinoid products effectively."
        }
    ]
    
    # Add categories to Firestore
    categories_ref = db_client.collection('categories')
    for category in categories:
        # Check if category already exists
        existing_category = list(categories_ref.where("id", "==", category["id"]).limit(1).stream())
        if not existing_category:
            categories_ref.document(category["id"]).set(category)
    
    # Create tags
    tags = [
        {"id": "beginner", "name": "Beginner Friendly"},
        {"id": "research", "name": "Research & Studies"},
        {"id": "products", "name": "Product Information"},
        {"id": "wellness", "name": "Wellness"},
        {"id": "pain-management", "name": "Pain Management"},
        {"id": "sleep", "name": "Sleep"},
        {"id": "inflammation", "name": "Inflammation"},
        {"id": "mental-health", "name": "Mental Health"}
    ]
    
    # Add tags to Firestore
    tags_ref = db_client.collection('tags')
    for tag in tags:
        # Check if tag already exists
        existing_tag = list(tags_ref.where("id", "==", tag["id"]).limit(1).stream())
        if not existing_tag:
            tags_ref.document(tag["id"]).set(tag)
    
    # Create articles
    articles = [
        {
            "slug": "cbd-beginners-guide",
            "title": "A Beginner's Guide to CBD",
            "subtitle": "Everything you need to know to get started with CBD products",
            "summary": "New to CBD? This comprehensive guide will help you understand what CBD is, how it works, and how to find the right products for your needs.",
            "content": """<h2>What is CBD?</h2><p>CBD, or cannabidiol, is a natural compound found in the cannabis plant. Unlike its cousin THC (tetrahydrocannabinol), CBD is non-intoxicating, meaning it won't cause a "high." This makes CBD an appealing option for people looking for relief from pain, anxiety, and sleep issues without the mind-altering effects of THC or certain pharmaceutical drugs.</p><p>CBD is just one of over 100 cannabinoids found in the cannabis plant. These compounds interact with the body's endocannabinoid system, which plays a role in regulating various physiological and cognitive processes.</p><h2>How Does CBD Work?</h2><p>Your body has an endocannabinoid system (ECS) that helps maintain homeostasis, or balance, across many bodily functions. The ECS consists of endocannabinoids (compounds your body naturally produces), receptors they bind to, and enzymes that break them down.</p><p>CBD interacts with this system in a more complex way than previously thought. Rather than binding directly to the main cannabinoid receptors (CB1 and CB2), CBD works indirectly, influencing the system's activity by:</p><ul><li>Inhibiting the enzymes that break down your body's own endocannabinoids, potentially prolonging their beneficial effects</li><li>Activating other receptors involved in pain and inflammation regulation, such as TRPV1 receptors</li><li>Affecting serotonin receptors, which play a role in mood and anxiety</li></ul><p>This multi-faceted action may explain why CBD shows promise for so many different conditions.</p><h2>Common Types of CBD Products</h2><p>The CBD market offers various products to suit different preferences and needs:</p><h3>CBD Oils and Tinctures</h3><p>These liquid extracts usually come in dropper bottles. You place drops under your tongue (sublingual administration) for faster absorption, or add them to food or drinks. Oils and tinctures are popular because they allow for precise dosing and relatively quick effects (typically 15-45 minutes).</p><h3>CBD Capsules and Edibles</h3><p>These provide a convenient, pre-measured dose of CBD. They must pass through your digestive system, so effects take longer to appear (usually 1-2 hours) but may last longer. Popular edible forms include gummies, chocolates, and baked goods.</p><h3>CBD Topicals</h3><p>Creams, balms, and lotions infused with CBD are applied directly to the skin. They're primarily used for localized relief of pain, inflammation, or skin conditions. Topicals don't enter the bloodstream significantly, so they're unlikely to produce whole-body effects.</p><h3>CBD Vape Products</h3><p>Inhaling vaporized CBD provides the fastest onset of effects (typically within minutes) but shorter duration. Note that vaping comes with its own health considerations and isn't recommended for everyone.</p><h2>Full-Spectrum, Broad-Spectrum, and Isolate</h2><p>When shopping for CBD, you'll encounter these terms describing the product's composition:</p><h3>Full-Spectrum CBD</h3><p>Contains all the cannabinoids naturally present in the cannabis plant, including trace amounts of THC (legally &lt;0.3%). Many users prefer full-spectrum products due to the "entourage effect" – the theory that cannabinoids work better together than in isolation.</p><h3>Broad-Spectrum CBD</h3><p>Contains multiple cannabinoids and other beneficial compounds but has THC removed. This option provides some of the entourage effect benefits while avoiding THC entirely.</p><h3>CBD Isolate</h3><p>Pure CBD with all other cannabinoids and compounds removed. Isolate is tasteless and odorless, making it versatile for adding to foods or other products. It's also preferred by those who want to avoid all other cannabinoids.</p><h2>How to Choose Quality CBD Products</h2><p>The CBD market is largely unregulated, making it crucial to shop wisely:</p><h3>Check for Third-Party Testing</h3><p>Reputable companies have their products tested by independent laboratories to verify potency and check for contaminants. Look for a Certificate of Analysis (COA) that you can review.</p><h3>Consider the Extraction Method</h3><p>CO₂ extraction is considered the gold standard for producing clean, potent CBD extracts without harmful residual solvents.</p><h3>Assess Transparency</h3><p>Quality brands are transparent about their hemp sourcing, manufacturing processes, and test results. They should provide clear information about the CBD content per serving.</p><h3>Read Reviews</h3><p>Customer reviews can provide insights into a product's effectiveness, though individual experiences vary considerably.</p><h2>Finding Your Optimal CBD Dosage</h2><p>There's no one-size-fits-all CBD dosage. The optimal amount depends on factors including:</p><ul><li>Your body weight and metabolism</li><li>The condition you're addressing</li><li>The product's potency</li><li>Your individual body chemistry</li></ul><p>Most experts recommend the "start low and go slow" approach:</p><ol><li>Begin with a low dose (5-10mg of CBD)</li><li>Maintain this dose for several days, noting any effects or side effects</li><li>If needed, gradually increase by 5mg every few days</li><li>Once you find a dose that works, stay there</li></ol><p>Keep a journal to track your dosage, when you take it, and the effects you experience. This can help you find your personal "sweet spot."</p><h2>Potential Benefits of CBD</h2><p>Research on CBD is still evolving, but preliminary studies and anecdotal evidence suggest potential benefits for:</p><ul><li><strong>Anxiety and stress:</strong> CBD may help reduce symptoms of general anxiety, social anxiety, and stress</li><li><strong>Pain and inflammation:</strong> Many users report relief from chronic pain and inflammatory conditions</li><li><strong>Sleep issues:</strong> CBD might help with both falling asleep and staying asleep</li><li><strong>Seizure disorders:</strong> The FDA has approved a CBD-based medication (Epidiolex) for certain forms of epilepsy</li></ul><p>Always consult with a healthcare provider before using CBD for any medical condition, especially if you take other medications.</p><h2>Possible Side Effects</h2><p>While CBD is generally well-tolerated, potential side effects may include:</p><ul><li>Dry mouth</li><li>Drowsiness or fatigue</li><li>Diarrhea</li><li>Reduced appetite</li><li>Interactions with certain medications</li></ul><p>CBD can affect how your liver metabolizes some medications, potentially increasing or decreasing their effectiveness. This is particularly important for medications with a "narrow therapeutic window."</p><h2>Legal Considerations</h2><p>While hemp-derived CBD containing less than 0.3% THC is federally legal in the US following the 2018 Farm Bill, state and local laws vary. Some states have restrictions on certain CBD products, particularly those added to food or marketed with health claims.</p><p>International laws regarding CBD vary significantly by country. Always check the current regulations in your location before purchasing or traveling with CBD products.</p><h2>Getting Started: Tips for CBD Beginners</h2><ul><li><strong>Consult a healthcare provider</strong> before starting CBD, especially if you have health conditions or take medications</li><li><strong>Research brands thoroughly</strong> and choose established companies with good reputations</li><li><strong>Start with a simple product</strong> like an oil or capsule before exploring other formats</li><li><strong>Be patient</strong> – CBD's effects can be subtle and may take time to become noticeable</li><li><strong>Keep a journal</strong> to track your experience, including dosage, timing, and effects</li></ul><p>Remember that while many people find CBD helpful, it's not a miracle cure. CBD works differently for everyone, and finding the right product and dosage for your needs may require some experimentation.</p><h2>Conclusion</h2><p>CBD offers an intriguing option for those seeking natural support for various health and wellness concerns. With proper research, quality products, and realistic expectations, CBD may become a valuable addition to your wellness routine.</p><p>As research continues to evolve, we'll gain better understanding of CBD's mechanisms and potential applications. For now, an informed, cautious approach is the best way to explore what CBD might offer you.</p>""",
            "featured_image": "https://images.unsplash.com/photo-1611075384322-403abcf7d8d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1611075384322-403abcf7d8d5?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["cbd-explained", "guides"],
            "tag_ids": ["beginner", "products"],
            "author_id": author_refs[1],
            "published_date": datetime.now() - timedelta(days=30),
            "reading_time": 10,
            "featured": True,
            "status": "published",
            "references": [
                "Pisanti S, et al. (2017). Cannabidiol: State of the art and new challenges for therapeutic applications. Pharmacology & Therapeutics.",
                "VanDolah HJ, et al. (2019). Clinicians' Guide to Cannabidiol and Hemp Oils. Mayo Clinic Proceedings.",
                "World Health Organization. (2018). Cannabidiol (CBD) Critical Review Report."
            ]
        },
        {
            "slug": "cbd-vs-cbg-cannabinoids-compared",
            "title": "CBD vs. CBG: Understanding the Differences",
            "subtitle": "A comparison of two prominent non-intoxicating cannabinoids",
            "summary": "Both CBD and CBG are non-intoxicating cannabinoids with therapeutic potential, but they have distinct differences. This article compares their effects, benefits, and applications to help you understand which might be right for you.",
            "content": """<h2>Introduction to Cannabinoids</h2><p>The cannabis plant contains over 100 different cannabinoids, each with unique properties and potential effects on the human body. While THC and CBD have received the most attention, other cannabinoids like CBG (Cannabigerol) are gaining recognition for their distinctive properties.</p><h2>What is CBG?</h2><p>CBG is often referred to as the 'mother cannabinoid' because other cannabinoids are derived from its precursor form, CBGA (cannabigerolic acid). As the cannabis plant matures, enzymes convert CBGA into THCA, CBDA, and other cannabinoid acids, which is why CBG is typically found in lower concentrations in mature plants.</p><h2>CBD vs. CBG: Chemical Structure</h2><p>Both CBD and CBG interact with the endocannabinoid system but have different molecular structures that influence how they bind to receptors. CBD has a weak affinity for both CB1 and CB2 receptors and works indirectly, often through other receptor systems. CBG, on the other hand, binds directly to both CB1 and CB2 receptors, potentially modulating the effects of other cannabinoids.</p><h2>Potential Benefits: How They Differ</h2><p>While research is still preliminary, especially for CBG, initial studies and anecdotal evidence suggest some differences in their potential therapeutic applications:</p><h3>CBD Potential Benefits:</h3><ul><li>Anxiety and stress reduction</li><li>Anti-inflammatory effects</li><li>Sleep support</li><li>Epilepsy management (FDA-approved for certain forms)</li><li>Pain management</li></ul><h3>CBG Potential Benefits:</h3><ul><li>Antibacterial properties (including against MRSA)</li><li>Neuroprotective effects</li><li>Appetite stimulation</li><li>Inflammatory bowel disease support</li><li>Bladder dysfunction reduction</li><li>Glaucoma treatment (reducing intraocular pressure)</li></ul><p>It's important to note that research on CBG is more limited than CBD, and many of these potential benefits require further study.</p><h2>Entourage Effect: Working Together</h2><p>Many experts believe in the 'entourage effect' - the theory that cannabinoids work better together than in isolation. Some products combine CBD and CBG to potentially enhance their therapeutic effects. Full-spectrum products contain multiple cannabinoids and may provide broader benefits than isolates.</p><h2>Choosing Between CBD and CBG</h2><p>When deciding which cannabinoid might be right for you, consider:</p><ul><li><strong>Your Specific Needs:</strong> Research which cannabinoid has shown promise for your particular concerns</li><li><strong>Product Availability:</strong> CBG products are less common and often more expensive</li><li><strong>Quality Indicators:</strong> Look for third-party testing regardless of which you choose</li><li><strong>Consider Combination Products:</strong> Products with both CBD and CBG may offer enhanced benefits</li></ul><h2>The Future of Cannabinoid Research</h2><p>As interest in non-intoxicating cannabinoids grows, so does research into their therapeutic potential. CBG represents just one of many cannabinoids being studied for their unique properties. The future may reveal more specific applications for different cannabinoids, leading to more targeted therapeutic uses.</p><h2>Conclusion</h2><p>Both CBD and CBG offer promising potential benefits with minimal side effects. While CBD currently has more research and wider availability, CBG is emerging as another valuable component of the cannabis plant. As with any supplement, consult with a healthcare professional before incorporating these cannabinoids into your wellness routine, especially if you take other medications.</p>""",
            "featured_image": "https://images.unsplash.com/photo-1579091372493-6616cf518f9b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1579091372493-6616cf518f9b?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["cbg-explained", "science"],
            "tag_ids": ["research", "beginner"],
            "author_id": author_refs[0],
            "published_date": datetime.now() - timedelta(days=15),
            "reading_time": 8,
            "featured": False,
            "status": "published",
            "references": [
                "Nachnani R, et al. (2021). The Pharmacological Case for Cannabigerol. Journal of Pharmacology and Experimental Therapeutics.",
                "Brierley DI, et al. (2017). Cannabigerol is a novel, well-tolerated appetite stimulant in pre-satiated rats. Psychopharmacology.",
                "Borrelli F, et al. (2013). Beneficial effect of the non-psychotropic plant cannabinoid cannabigerol on experimental inflammatory bowel disease. Biochemical Pharmacology."
            ]
        },
        {
            "slug": "cannabinoids-for-sleep-improvement",
            "title": "Using Cannabinoids for Better Sleep: A Comprehensive Guide",
            "subtitle": "How CBD, CBN, and other compounds may help improve sleep quality",
            "summary": "Sleep issues affect millions of people worldwide. This guide explores how cannabinoids like CBD and CBN may help address sleep problems, what the research says, and how to incorporate them into your sleep routine effectively.",
            "content": """<h2>The Importance of Quality Sleep</h2><p>Quality sleep is essential for physical health, cognitive function, emotional wellbeing, and overall quality of life. Unfortunately, sleep problems are increasingly common, with an estimated 50-70 million US adults suffering from sleep disorders.</p><p>While traditional sleep aids can be effective, many people experience unwanted side effects or prefer natural alternatives. This has led to growing interest in cannabinoids as potential sleep aids.</p><h2>How Cannabinoids May Influence Sleep</h2><p>The endocannabinoid system (ECS) plays a role in regulating sleep and other bodily functions. Plant cannabinoids (phytocannabinoids) can interact with this system, potentially influencing sleep in several ways:</p><ul><li>Addressing underlying issues that disrupt sleep (pain, anxiety)</li><li>Interacting with receptors involved in sleep regulation</li><li>Affecting REM and deep sleep phases</li><li>Potentially helping reset disrupted sleep cycles</li></ul><h2>Key Cannabinoids for Sleep</h2><h3>CBD (Cannabidiol)</h3><p>CBD may help with sleep primarily by addressing factors that interfere with quality rest:</p><ul><li><strong>Anxiety reduction:</strong> CBD has shown anxiolytic properties, potentially calming racing thoughts that prevent sleep</li><li><strong>Pain management:</strong> By reducing discomfort, CBD may make it easier to fall and stay asleep</li><li><strong>Cortisol regulation:</strong> Preliminary research suggests CBD may influence cortisol levels, a stress hormone that impacts sleep quality</li></ul><p>Interestingly, CBD may promote alertness in low doses while supporting deeper sleep in higher doses, though individual responses vary significantly.</p><h3>CBN (Cannabinol)</h3><p>Often marketed specifically as a sleep aid, CBN is created when THC oxidizes (ages). While anecdotal reports suggest strong sedative effects, scientific evidence is still limited. CBN's sleep-promoting effects may be enhanced when combined with other cannabinoids and terpenes.</p><h3>THC (Tetrahydrocannabinol)</h3><p>In legal markets, some products contain low doses of THC for sleep. THC can have sedative effects and may reduce the time it takes to fall asleep. However, it can disrupt REM sleep with regular use and may cause hangover-like effects in some individuals.</p><h2>Finding Your Optimal Approach</h2><p>Cannabinoids affect individuals differently based on factors including:</p><ul><li>Body chemistry</li><li>Sleep issue type</li><li>Dosage</li><li>Product formulation</li><li>Timing of administration</li></ul><p>There's no one-size-fits-all recommendation, so finding the right approach may require experimentation. Consider these guidelines:</p><h3>Starting with CBD</h3><ul><li>Begin with 10-25mg before bed</li><li>Gradually increase if needed</li><li>Try broad-spectrum or full-spectrum products for enhanced effects</li><li>Allow 1-2 weeks of consistent use to evaluate effects</li></ul><h3>Timing Considerations</h3><p>The best time to take cannabinoids for sleep depends on your specific sleep issues:</p><ul><li><strong>Trouble falling asleep:</strong> 30-60 minutes before bedtime</li><li><strong>Difficulty staying asleep:</strong> Consider longer-acting formats like capsules or edibles</li><li><strong>Early waking:</strong> Slightly higher doses or timed-release formulations</li></ul><h2>Product Types for Sleep</h2><p>Different delivery methods offer varying onset times and durations:</p><ul><li><strong>Oils/Tinctures:</strong> Mid-range onset (15-45 minutes), moderate duration (4-6 hours)</li><li><strong>Capsules/Edibles:</strong> Slower onset (30-90 minutes), longer duration (6-8 hours)</li><li><strong>Vaporized:</strong> Rapid onset (almost immediate), shorter duration (2-4 hours)</li><li><strong>Specialized Sleep Formulas:</strong> Often combine cannabinoids with sleep-promoting herbs or melatonin</li></ul><h2>Creating a Sleep-Promoting Routine</h2><p>Cannabinoids work best as part of a comprehensive sleep hygiene approach:</p><ul><li>Maintain a consistent sleep schedule</li><li>Limit screen time before bed (blue light exposure)</li><li>Create a comfortable, dark, cool sleeping environment</li><li>Avoid caffeine, large meals, and alcohol near bedtime</li><li>Consider relaxation practices like meditation or gentle yoga</li></ul><h2>Safety Considerations</h2><p>While cannabinoids are generally well-tolerated, consider these factors:</p><ul><li>Potential drowsiness (don't drive or operate machinery until you know how you respond)</li><li>Possible interactions with medications</li><li>Quality and testing of products</li><li>Legal status in your location</li></ul><p>Always consult a healthcare provider before using cannabinoids for sleep, especially if you have existing health conditions or take medications.</p><h2>Conclusion: A Personalized Approach</h2><p>Cannabinoids offer promising potential for sleep support, but finding the right approach requires patience and personalization. Start with high-quality products, conservative dosing, and careful attention to how your body responds. Combined with good sleep hygiene practices, cannabinoids may become a valuable part of your sleep wellness routine.</p>""",
            "featured_image": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["wellness", "guides"],
            "tag_ids": ["sleep", "research", "wellness"],
            "author_id": author_refs[2],
            "published_date": datetime.now() - timedelta(days=7),
            "reading_time": 12,
            "featured": True,
            "status": "published",
            "references": [
                "Shannon S, et al. (2019). Cannabidiol in Anxiety and Sleep: A Large Case Series. The Permanente Journal.",
                "Babson KA, et al. (2017). Cannabis, Cannabinoids, and Sleep: a Review of the Literature. Current Psychiatry Reports.",
                "Chagas MH, et al. (2014). Effects of acute systemic administration of cannabidiol on sleep-wake cycle in rats. Journal of Psychopharmacology."
            ]
        },
        {
            "slug": "cannabinoids-for-pain-management",
            "title": "Cannabinoids for Pain Management: What the Science Says",
            "subtitle": "Exploring the evidence behind using cannabinoids for different types of pain",
            "summary": "Pain relief is one of the most common reasons people turn to cannabinoids. This article examines the scientific evidence behind using CBD, THC, and other cannabinoids for different types of pain, including chronic pain, neuropathic pain, and inflammatory pain.",
            "content": """<h2>Understanding Pain and the Endocannabinoid System</h2><p>Pain is a complex biological and psychological experience. It serves as an important warning system, but chronic pain can become debilitating and significantly impact quality of life. The endocannabinoid system (ECS) is involved in regulating pain sensation, making cannabinoids potentially valuable tools for pain management.</p><p>Your body naturally produces endocannabinoids, which interact with cannabinoid receptors (CB1 and CB2) throughout your nervous system and immune cells. Plant-derived cannabinoids (phytocannabinoids) can similarly influence this system, potentially modulating pain signals and inflammatory responses.</p><h2>The Evidence for Cannabinoids in Pain Management</h2><p>Research into cannabinoids for pain management has produced promising but sometimes mixed results. Here's what current evidence suggests for different pain types:</p><h3>Chronic Pain</h3><p>A 2018 review published in the Cochrane Database of Systematic Reviews found that cannabinoids might be effective for chronic neuropathic pain. However, the quality of evidence was rated as moderate or low.</p><p>More encouragingly, a 2021 observational study of 97 patients using CBD-rich treatments found that over half experienced improved pain by 30% or more, with minimal adverse effects.</p><h3>Neuropathic Pain</h3><p>Neuropathic pain (resulting from nerve damage) is often difficult to treat with conventional medications. Multiple studies suggest cannabinoids may help with this type of pain. A meta-analysis in the Journal of Pain found that cannabinoids significantly reduced chronic neuropathic pain intensity compared to placebo.</p><h3>Inflammatory Pain</h3><p>CBD in particular has shown anti-inflammatory properties in multiple studies. By reducing inflammation, CBD and other cannabinoids may indirectly help with pain caused by inflammatory conditions like arthritis. A 2016 study using a topical CBD gel on rats with arthritis showed reduced joint swelling and pain behaviors.</p><h3>Cancer-Related Pain</h3><p>Some studies suggest cannabinoids may help with pain related to cancer and cancer treatments. A study published in the Journal of Pain and Symptom Management found that a THC:CBD extract was more effective than THC alone or placebo in patients with intractable cancer-related pain.</p><h2>Different Cannabinoids for Pain</h2><p>Various cannabinoids may affect pain through different mechanisms:</p><h3>CBD (Cannabidiol)</h3><p>CBD doesn't bind directly to cannabinoid receptors but appears to work through several mechanisms:</p><ul><li>Preventing the breakdown of endocannabinoids, enhancing their effect</li><li>Activating TRPV1 receptors involved in pain and inflammation</li><li>Reducing inflammatory signaling molecules</li><li>Potentially affecting glycine receptors that play a role in pain processing</li></ul><p>CBD has the advantage of providing potential pain relief without intoxicating effects.</p><h3>THC (Tetrahydrocannabinol)</h3><p>THC binds directly to CB1 receptors in the nervous system, which may:</p><ul><li>Alter pain perception in the brain</li><li>Reduce pain signal transmission</li><li>Provide mild sedative effects that may help with pain-induced sleep issues</li></ul><p>However, THC produces psychoactive effects and is subject to stricter regulations.</p><h3>Minor Cannabinoids with Potential</h3><p>Emerging research suggests other cannabinoids may also have pain-relieving properties:</p><ul><li><strong>CBG (Cannabigerol):</strong> May have anti-inflammatory and analgesic properties</li><li><strong>CBC (Cannabichromene):</strong> Shows potential for reducing inflammatory pain</li><li><strong>THCV (Tetrahydrocannabivarin):</strong> May affect pain perception without strong psychoactive effects</li></ul><h2>Application Methods for Pain Relief</h2><p>The best application method depends on the type of pain being treated:</p><h3>Topicals</h3><p>Creams, balms, and lotions work well for localized pain like arthritis, muscle soreness, or peripheral neuropathy. They allow direct application to the affected area without systemic effects. CBD and other cannabinoids in topicals interact with cannabinoid receptors in the skin.</p><h3>Oral/Sublingual</h3><p>Oils and tinctures taken sublingually (under the tongue) provide faster and more consistent absorption than edibles. This method is suitable for whole-body pain or conditions affecting multiple areas.</p><h3>Inhalation</h3><p>Vaporized cannabinoids provide the quickest onset of effects, making this method suitable for acute pain episodes that require rapid relief. However, effects are shorter-lasting compared to other methods.</p><h3>Edibles and Capsules</h3><p>These offer longer-lasting effects, which can be beneficial for chronic pain management. The slower onset makes them less suitable for breakthrough pain.</p><h2>Dosing Considerations</h2><p>Appropriate dosing for pain management varies considerably between individuals. Factors affecting optimal dosage include:</p><ul><li>Pain severity and type</li><li>Individual endocannabinoid system function</li><li>Previous cannabinoid experience</li><li>Body weight and metabolism</li><li>Concurrent medications</li></ul><p>A common approach is to "start low and go slow" - beginning with a minimal dose and gradually increasing until finding the optimal balance between pain relief and minimal side effects.</p><h2>Potential Concerns and Side Effects</h2><p>While cannabinoids are generally well-tolerated, potential side effects may include:</p><ul><li>Drowsiness and fatigue</li><li>Dry mouth</li><li>Changes in appetite</li><li>Diarrhea (particularly with high-dose CBD)</li><li>Psychoactive effects (with THC)</li><li>Potential drug interactions</li></ul><p>Patients taking blood thinners, antiepileptic drugs, or certain antidepressants should consult healthcare providers before using cannabinoids due to potential interactions.</p><h2>Integrating Cannabinoids into Pain Management</h2><p>Most pain management experts view cannabinoids as potential components of a comprehensive approach rather than standalone treatments. Consider:</p><ul><li>Using cannabinoids alongside conventional treatments under medical supervision</li><li>Combining with other evidence-based approaches like physical therapy and pain psychology</li><li>Tracking results systematically to determine effectiveness</li><li>Adjusting dosage and cannabinoid types based on response</li></ul><h2>Conclusion: Promising but Still Developing</h2><p>The evidence for cannabinoids in pain management is promising but still evolving. Individual responses vary significantly, and what works for one person may not work for another. For those considering cannabinoids for pain, working with knowledgeable healthcare providers and approaching treatment methodically offers the best chance of success.</p><p>As research continues to develop, we'll gain better understanding of which cannabinoids, formulations, and dosing protocols work best for specific pain conditions.</p>""",
            "featured_image": "https://images.unsplash.com/photo-1595268746332-090e6b5fb9a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1595268746332-090e6b5fb9a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["science", "wellness"],
            "tag_ids": ["pain-management", "inflammation", "research"],
            "author_id": author_refs[0],
            "published_date": datetime.now() - timedelta(days=10),
            "reading_time": 15,
            "featured": False,
            "status": "published",
            "references": [
                "Aviram J, Samuelly-Leichtag G. (2017). Efficacy of Cannabis-Based Medicines for Pain Management: A Systematic Review and Meta-Analysis of Randomized Controlled Trials. Pain Physician.",
                "Hammell DC, et al. (2016). Transdermal cannabidiol reduces inflammation and pain-related behaviours in a rat model of arthritis. European Journal of Pain.",
                "National Academies of Sciences, Engineering, and Medicine. (2017). The Health Effects of Cannabis and Cannabinoids: The Current State of Evidence and Recommendations for Research."
            ]
        },
        {
            "slug": "how-to-read-cbd-lab-reports",
            "title": "How to Read and Understand CBD Lab Reports",
            "subtitle": "A guide to interpreting certificates of analysis for informed decisions",
            "summary": "Third-party lab testing is essential for ensuring CBD product quality and safety, but understanding these reports can be challenging. This guide explains how to read certificates of analysis (COAs), what to look for, and red flags that might indicate quality issues.",
            "content": """<h2>Why Lab Testing Matters</h2><p>As the CBD industry continues to grow, third-party lab testing has become an essential component of product quality and safety. Unlike many supplements, CBD products are not consistently regulated by the FDA, making independent lab verification crucial for consumers.</p><p>A Certificate of Analysis (COA) from an independent laboratory provides objective information about a product's cannabinoid content, potential contaminants, and overall quality. Learning to read these reports empowers you to make informed decisions about the products you purchase.</p><h2>Finding the COA</h2><p>Reputable CBD companies typically make their lab reports readily available through:</p><ul><li>QR codes on product packaging</li><li>Dedicated sections on their websites</li><li>Upon request via customer service</li></ul><p>If a company cannot or will not provide recent lab reports, this should be considered a serious red flag. Transparency is a hallmark of quality in the CBD industry.</p><h2>Understanding the Basic Sections of a COA</h2><p>A comprehensive Certificate of Analysis typically includes several sections:</p><h3>1. Product and Laboratory Information</h3><p>The header should include:</p><ul><li>Name and contact information of the testing laboratory</li><li>The manufacturer/company that submitted the sample</li><li>Sample identification (batch/lot number)</li><li>Date of sample collection and testing</li><li>Product name</li></ul><p>Verify that the product name and batch number match what's on your product packaging.</p><h3>2. Cannabinoid Profile</h3><p>This section details the concentrations of various cannabinoids, including:</p><ul><li>CBD (Cannabidiol)</li><li>THC (Tetrahydrocannabinol)</li><li>Minor cannabinoids like CBG, CBN, CBC, etc.</li></ul><p>Cannabinoid content is typically reported in percentages (%) and/or milligrams per gram (mg/g). For finished products like tinctures, it may be reported as milligrams per milliliter (mg/mL) or total milligrams in the container.</p><h3>3. Terpene Profile (if tested)</h3><p>Some more comprehensive COAs include terpene analysis, listing the aromatic compounds that contribute to the product's effects and aroma.</p><h3>4. Contaminant Testing</h3><p>Quality COAs should include testing for:</p><ul><li><strong>Residual solvents:</strong> Chemicals used in extraction</li><li><strong>Pesticides:</strong> Agricultural chemicals used during cultivation</li><li><strong>Heavy metals:</strong> Lead, arsenic, mercury, cadmium</li><li><strong>Microbials:</strong> Bacteria, mold, yeast</li><li><strong>Mycotoxins:</strong> Toxic compounds produced by fungi</li></ul><p>Each section will typically indicate whether levels are above or below the detection limit or safety threshold.</p><h2>How to Verify Cannabinoid Content</h2><p>When checking cannabinoid content, pay particular attention to:</p><h3>CBD Content</h3><p>Verify that the CBD content matches what's advertised on the product label. A slight variation (±10%) is normal, but significant discrepancies indicate quality control issues.</p><p>For example, if a product claims to contain 1000mg of CBD, the lab report should show approximately 900-1100mg total CBD.</p><h3>THC Content</h3><p>For legal hemp-derived products, THC content must be 0.3% or less by dry weight. Confirm this on the report, especially if you're concerned about THC exposure.</p><h3>Spectrum Type</h3><p>The cannabinoid profile should match the product's claimed spectrum type:</p><ul><li><strong>Full-spectrum:</strong> Should show detectable amounts of multiple cannabinoids including trace THC</li><li><strong>Broad-spectrum:</strong> Should show multiple cannabinoids but non-detectable or trace amounts of THC</li><li><strong>CBD isolate:</strong> Should show 98%+ CBD with minimal or no other cannabinoids</li></ul><h2>Reading Contaminant Test Results</h2><p>Contaminant sections typically show:</p><ul><li>The substance tested for</li><li>The amount detected (if any)</li><li>The "Limit of Quantitation" (LOQ) - the smallest amount the test can reliably detect</li><li>The "Action Level" or acceptable limit</li><li>Pass/Fail status</li></ul><p>Ideally, results should show "ND" (Not Detected) or values below the action level for all contaminants.</p><h3>Heavy Metals</h3><p>Common heavy metals tested include lead, arsenic, mercury, and cadmium. These are particularly important to check because hemp plants can absorb heavy metals from soil (a process called phytoremediation).</p><h3>Pesticides</h3><p>The pesticide panel should test for common agricultural chemicals. This is especially important because hemp is often grown as a bioaccumulator that absorbs substances from the soil.</p><h3>Residual Solvents</h3><p>This tests for remnants of chemicals used during extraction. Common solvents include ethanol, butane, propane, and others. CO2 extraction typically doesn't leave behind solvent residues.</p><h3>Microbial Testing</h3><p>This section checks for harmful microorganisms like E. coli, salmonella, and aspergillus. Some amount of total yeast and mold is normal, but pathogenic bacteria should be absent.</p><h2>Red Flags to Watch For</h2><p>When reviewing a COA, be alert for these warning signs:</p><ul><li><strong>Outdated testing:</strong> Reports should be for the specific batch you're purchasing and relatively recent</li><li><strong>Missing sections:</strong> Comprehensive testing should include cannabinoid profile AND contaminant screening</li><li><strong>Significant potency discrepancies:</strong> Large differences between labeled and actual CBD content</li><li><strong>Testing performed by the manufacturer:</strong> Testing should be conducted by an independent third-party lab</li><li><strong>Inconsistent batch numbers:</strong> The batch/lot number on the report should match your product</li><li><strong>Failed contaminant tests:</strong> Any "Fail" results in the contaminant sections are concerning</li></ul><h2>Additional Tips for Evaluation</h2><ul><li><strong>Check lab credentials:</strong> The testing laboratory should be accredited (look for ISO 17025 certification)</li><li><strong>Compare products:</strong> Use COAs to compare CBD cost per milligram across products</li><li><strong>Consider full panels:</strong> More comprehensive testing generally indicates a company's commitment to quality</li><li><strong>Look for QR codes:</strong> Many quality products now include scannable codes linking directly to batch-specific COAs</li></ul><h2>Conclusion</h2><p>While COAs may seem technical at first glance, they provide valuable information about the products you're putting in your body. Taking time to understand lab reports allows you to verify that you're getting what you pay for and avoid potentially harmful contaminants.</p><p>Remember that reputable companies are proud of their testing results and make them easily accessible. If you're ever unsure about interpreting a specific lab report, don't hesitate to contact the company directly for clarification.</p>""",
            "featured_image": "https://images.unsplash.com/photo-1584362917165-526a968579e8?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
            "thumbnail": "https://images.unsplash.com/photo-1584362917165-526a968579e8?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80",
            "category_ids": ["guides", "science"],
            "tag_ids": ["products", "beginner"],
            "author_id": author_refs[1],
            "published_date": datetime.now() - timedelta(days=20),
            "reading_time": 10,
            "featured": False,
            "status": "published",
            "references": [
                "Bonn-Miller MO, et al. (2017). Labeling Accuracy of Cannabidiol Extracts Sold Online. JAMA.",
                "FDA. (2020). What You Need to Know (And What We're Working to Find Out) About Products Containing Cannabis or Cannabis-derived Compounds, Including CBD.",
                "Pavlovic R, et al. (2018). Quality Traits of \"Cannabidiol Oils\": Cannabinoids Content, Terpene Fingerprint and Oxidation Stability of European Commercially Available Preparations. Molecules."
            ]
        }
    ]
    
    # Add articles to Firestore
    articles_batch = db_client.batch()
    for article in articles:
        # Create a new doc reference without setting data yet
        doc_ref = articles_ref.document()
        # Add data with the ID included
        article_data = article.copy()
        article_data["id"] = doc_ref.id
        articles_batch.set(doc_ref, article_data)
    
    # Commit the batch
    articles_batch.commit()
    
    # Return success response
    return SeedArticlesResponse(
        message="Successfully seeded the database with articles, categories, and tags.",
        count=len(articles),
        categories_count=len(categories),
        tags_count=len(tags),
        authors_count=len(authors))
