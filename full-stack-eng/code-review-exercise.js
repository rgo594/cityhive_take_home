class Product extends Base {
  constructor(...stuff) {
    Object.assign(this, ...stuff)
  }

  private get name() {
    this.name
  }

  static toNames(products) {
    return products.map(toName)
  }

  static prefetch(urls) {
    let products = []
    urls.map(url => new Product(url)).forEach(this.call()).forEach((p) => {
      products.push(p)
    })
  }

  toName(product) {
    return product.name
  }
  
  //(❓ for candidate) why do we use underscore in the method name? what's the pattern here?
  _call() {
    let resp = fetch(this.url)
    if (!resp.ok) return

    json = resp.json()
    console.log("got product")
    if (json.status === 1) this.STATUS = "available"
    if (json.status === 2) this.STATUS = "out of Stock"
    Object.assign(this, json)
  }

  get price = () => {
    return this._price || this.price
  }
}