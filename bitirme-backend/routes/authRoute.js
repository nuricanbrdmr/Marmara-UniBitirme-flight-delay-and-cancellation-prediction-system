import express from "express";
import * as authController from "../controllers/authController.js";

const router = express.Router();

router.route("/register").post(authController.register);
router.route("/login").post(authController.login);
router.route("/refreshToken").post(authController.refreshToken);
router.route("/sendResetMail").post(authController.sendResetMail);
router.route("/resetPassword").post(authController.resetPassword);

export default router;
