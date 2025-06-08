import express from "express";
import * as locationController from "../controllers/locationController.js";

const router = express.Router();

router.route("/countries").get(locationController.getCountryUs);
router.route("/cities").get(locationController.getCitiesJson);
router.route("/airports").get(locationController.getAirports);
router.route("/cityPhoto").get(locationController.getCityPhotos);
router.route("/airportByCode").get(locationController.getAirportByCode);

export default router;
