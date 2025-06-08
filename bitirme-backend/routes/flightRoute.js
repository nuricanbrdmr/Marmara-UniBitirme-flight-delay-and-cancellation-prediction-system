import express from "express";
import * as flightController from "../controllers/flightController.js";

const router = express.Router();

router.route("/oneWay").get(flightController.getOneWay);
router.route("/oneWay7DaysMinPrice").get(flightController.getOneWay7DaysMinPrice);
router.route("/predict").post(flightController.predictFlight);

export default router;
