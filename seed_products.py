import requests
import os
from app import app, db, Product

# Data extracted from Instagram
posts = [
  {
    "title": "Roselume Collection",
    "price": "Check on Instagram",
    "instagram_url": "https://www.instagram.com/svara.in_/reel/DTk2WlxDZhY/",
    "image_url": "https://instagram.fcok9-1.fna.fbcdn.net/v/t51.2885-15/616987872_17848878390664310_4052406002057356443_n.jpg?stp=dst-jpg_e35_p640x640_sh0.08_tt6&_nc_ht=instagram.fcok9-1.fna.fbcdn.net&_nc_cat=102&_nc_oc=Q6cZ2QHcQvQbG-1L0FHt9p1DFyECVSuGByhbrMnKKSXBJhlLfbL4n2n0cMVspu-FbEnq9no&_nc_ohc=30gCvX2QZ1sQ7kNvwFGAEh8&_nc_gid=6vCASzmXsA9fvus0xvbaMQ&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfpXTKZrGJ8sudAuvCTEEkc5KZteU_Aks-WkAIgTQiNZpw&oe=6970278F&_nc_sid=8b3546",
    "filename": "roselume.jpg",
    "description": "Roselume ✨- A soft bloom of light, designed to shine every day."
  },
  {
    "title": "Vintage Vibe",
    "price": "Check on Instagram",
    "instagram_url": "https://www.instagram.com/svara.in_/p/DTk0I3hjRiV/",
    "image_url": "https://instagram.fcok9-1.fna.fbcdn.net/v/t51.2885-15/618314199_17848870950664310_371217110699451352_n.jpg?stp=dst-jpg_e35_p640x640_sh0.08_tt6&_nc_ht=instagram.fcok9-1.fna.fbcdn.net&_nc_cat=102&_nc_oc=Q6cZ2QHcQvQbG-1L0FHt9p1DFyECVSuGByhbrMnKKSXBJhlLfbL4n2n0cMVspu-FbEnq9no&_nc_ohc=P_YNsvd_MRQQ7kNvwGrcnkj&_nc_gid=6vCASzmXsA9fvus0xvbaMQ&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfpE2PUi-Gh3Msp3Y4rMHQxI8shvb3qjTOBndrHXf1Iw1A&oe=697020C5&_nc_sid=8b3546",
    "filename": "vintage.jpg",
    "description": "Daily inspiration from Svara."
  },
  {
    "title": "Svara Classics",
    "price": "Check on Instagram",
    "instagram_url": "https://www.instagram.com/svara.in_/p/DTiQZ1_k9jH/",
    "image_url": "https://instagram.fcok9-1.fna.fbcdn.net/v/t51.2885-15/617469835_17848612350664310_8736313590814333598_n.jpg?stp=dst-jpg_e35_p640x640_sh0.08_tt6&_nc_ht=instagram.fcok9-1.fna.fbcdn.net&_nc_cat=102&_nc_oc=Q6cZ2QHcQvQbG-1L0FHt9p1DFyECVSuGByhbrMnKKSXBJhlLfbL4n2n0cMVspu-FbEnq9no&_nc_ohc=Q4A4X237iI0Q7kNvwH2cWaG&_nc_gid=6vCASzmXsA9fvus0xvbaMQ&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_Afo-GMSTeSZpcFVcvgyyvwBQxCkpaZ0LUPLkz5gbxi7tVQ&oe=69703CA5&_nc_sid=8b3546",
    "filename": "classics.jpg",
    "description": "Handpicked favorites for you."
  },
  {
    "title": "Ivora Collection",
    "price": "Check on Instagram",
    "instagram_url": "https://www.instagram.com/svara.in_/reel/DTiNzPtk1g2/",
    "image_url": "https://instagram.fcok9-1.fna.fbcdn.net/v/t51.2885-15/613200848_1357573892791160_5302975607912437259_n.jpg?stp=dst-jpg_e15_tt6&_nc_ht=instagram.fcok9-1.fna.fbcdn.net&_nc_cat=108&_nc_oc=Q6cZ2QHcQvQbG-1L0FHt9p1DFyECVSuGByhbrMnKKSXBJhlLfbL4n2n0cMVspu-FbEnq9no&_nc_ohc=FTdQBX-iF9kQ7kNvwFRr4B5&_nc_gid=6vCASzmXsA9fvus0xvbaMQ&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfpiVaEpwN4fEK3eA4cVlWnikjwzSxAmM9UDtj1udAzwng&oe=6970214F&_nc_sid=8b3546",
    "filename": "ivora.jpg",
    "description": "Ivora✨– evokes ivory glow and quiet luxury. 🤍"
  },
  {
    "title": "New Arrival",
    "price": "Check on Instagram",
    "instagram_url": "https://www.instagram.com/svara.in_/reel/DTdUUYtE_n9/",
    "image_url": "https://instagram.fcok9-1.fna.fbcdn.net/v/t51.2885-15/616043353_745170364854321_6788671037887919583_n.jpg?stp=dst-jpg_e15_tt6&_nc_ht=instagram.fcok9-1.fna.fbcdn.net&_nc_cat=109&_nc_oc=Q6cZ2QHcQvQbG-1L0FHt9p1DFyECVSuGByhbrMnKKSXBJhlLfbL4n2n0cMVspu-FbEnq9no&_nc_ohc=B2VqfG2fg2oQ7kNvwFJCcFk&_nc_gid=6vCASzmXsA9fvus0xvbaMQ&edm=AOQ1c0wBAAAA&ccb=7-5&oh=00_AfrerN4y20fNTgyEjwxrcWzRy1xPBY4LTw-qOPsFjL4yOw&oe=69704489&_nc_sid=8b3546",
    "filename": "arrival.jpg",
    "description": "A new voice is on its way. SVARA Coming soon ✨"
  }
]

def seed():
    with app.app_context():
        # Clear existing products
        Product.query.delete()
        
        # Download images and add products
        for post in posts:
            print(f"Downloading image for {post['title']}...")
            try:
                response = requests.get(post['image_url'])
                if response.status_code == 200:
                    image_path = os.path.join(app.config['UPLOAD_FOLDER'], post['filename'])
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    
                    new_product = Product(
                        name=post['title'],
                        description=post['description'],
                        price=post['price'],
                        image_file=post['filename'],
                        instagram_url=post['instagram_url']
                    )
                    db.session.add(new_product)
                else:
                    print(f"Failed to download image for {post['title']}")
            except Exception as e:
                print(f"Error processing {post['title']}: {e}")
        
        db.session.commit()
        print("Database seeded successfully!")

if __name__ == '__main__':
    seed()
