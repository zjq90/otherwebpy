/**
 * API统一导出
 */

import auth from "./auth";
import card from "./card";
import order from "./order";
import consumption from "./consumption";

export { auth, card, order, consumption };

export default {
  auth,
  card,
  order,
  consumption
};
