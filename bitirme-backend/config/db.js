import mongoose from "mongoose"
import dotenv from "dotenv";

dotenv.config();

const connectDb = async () => {
    try {
        await mongoose.connect(process.env.MONGODB_URI);
        console.log('Mongodb connection has been established!')
    } catch (error) {
        console.log('MongoDb connection has failed', error.message);
    }
}

export default connectDb;