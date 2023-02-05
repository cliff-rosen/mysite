export function setExpiringLocalStorageItem(key, value, expirationInMinutes) {
  const expirationTime = Date.now() + expirationInMinutes * 60000; // 60000 is the number of milliseconds in a minute
  const expiringItem = {
    value: value,
    expiration: expirationTime,
  };
  localStorage.setItem(key, JSON.stringify(expiringItem));
}

export function getExpiringLocalStorageItem(key) {
  const expiringItem = JSON.parse(localStorage.getItem(key));
  console.log(expiringItem);
  if (
    expiringItem &&
    expiringItem.expiration &&
    expiringItem.expiration > Date.now()
  ) {
    return expiringItem.value;
  } else {
    localStorage.removeItem(key);
    return null;
  }
}
