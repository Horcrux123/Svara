import instaloader
import os
from werkzeug.utils import secure_filename
from app import app, db, Product

def sync_instagram_posts(limit=5):
    """
    Fetches the latest posts from Instagram and adds them as products if they don't exist.
    """
    print("Starting Instagram Sync...")
    
    # Needs app context effectively to access DB
    with app.app_context():
        L = instaloader.Instaloader()
        
        try:
            profile = instaloader.Profile.from_username(L.context, 'svara.in_')
            
            count = 0
            for post in profile.get_posts():
                if count >= limit:
                    break
                    
                post_url = f"https://www.instagram.com/p/{post.shortcode}/"
                
                # Check for duplicates more robustly using the shortcode
                # We search if any existing product's instagram_url contains this shortcode
                exists = Product.query.filter(Product.instagram_url.contains(post.shortcode)).first()
                
                if exists:
                    print(f"Skipping {post.shortcode}: Already exists.")
                    continue

                # It's a new post!
                print(f"Processing new post: {post.shortcode}")
                
                # Download Image
                filename = f"{post.shortcode}.jpg"
                target_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Download logic...
                # Using simple requests for image content as before
                import requests
                try:
                    img_data = requests.get(post.url).content
                    with open(target_path, 'wb') as handler:
                        handler.write(img_data)
                except Exception as e:
                    print(f"Failed to download image for {post.shortcode}: {e}")
                    continue

                # Create Product
                caption = post.caption if post.caption else "New arrival from Svara."
                title = "New Arrival"
                if caption:
                    lines = caption.split('\n')
                    for line in lines:
                        clean_line = line.strip()
                        if clean_line and len(clean_line) < 30 and '#' not in clean_line:
                            title = clean_line
                            break
                
                new_product = Product(
                    name=title, 
                    description=caption[:500], 
                    price="Check Instagram", 
                    image_file=filename,
                    instagram_url=post_url
                )
                
                db.session.add(new_product)
                count += 1
                
            db.session.commit()
            return True, f"Synced {count} new products."
            
        except Exception as e:
            print(f"Error syncing: {e}")
            return False, str(e)
