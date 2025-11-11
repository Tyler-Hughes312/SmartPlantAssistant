# Create .env file on Raspberry Pi

Run this command on your Raspberry Pi:

```bash
cd ~/smart_plant_pi
cat > .env << 'EOF'
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
PLANT_ID=1
EOF
```

Then verify it was created:
```bash
cat .env
```

You should see:
```
DATABASE_URL=postgresql://username:password@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
PLANT_ID=1
```

