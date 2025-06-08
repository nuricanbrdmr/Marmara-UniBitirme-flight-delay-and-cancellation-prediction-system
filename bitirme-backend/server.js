import express from "express";
import authRoute from "./routes/authRoute.js";
import locationRoute from "./routes/locationRoute.js";
import flightRoute from "./routes/flightRoute.js";
import connectDb from "./config/db.js";
import cors from "cors";

const app = express();
const port = 3000;

const corsOption = {
  origin: ["http://localhost:5173"],
  credentials: true,
};

app.use(cors(corsOption));
app.use(express.json());

app.use("/api/v1/auth", authRoute);
app.use("/api/v1/location", locationRoute);
app.use("/api/v1/flight", flightRoute);

try {
  await connectDb();
  app.listen(port, () => {
    console.log("server is listening on port: ", port);
  });
} catch (error) {
  console.error("Database connection error:", error);
  process.exit(1);
}
