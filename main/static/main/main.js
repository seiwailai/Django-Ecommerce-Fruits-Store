const carouselContainer = document.getElementById('carousel-container');
const carouselImages = document.querySelectorAll('.carousel-slide img');
const carouselPreviousButton = document.querySelector('#previous-btn');
const carouselNextButton = document.querySelector('#next-btn');
const updateCart = document.querySelectorAll('.update-cart');
const updateItem = document.querySelectorAll('.update-item');
let counter = 1;

if (carouselContainer){
    let size = carouselImages[0].clientWidth;

    carouselSlide.style.transform = 'translateX(' + (-size) + 'px)'

    function changeSlide(counter) {
        carouselSlide.style.transition = 'transform 0.3s ease-in-out';
        resize(counter);
        carouselContainer.style.width = `${carouselImages[counter].clientWidth}px`;
        carouselSlide.style.transform = 'translateX(' + (-size) + 'px)';
    }

    function resize(counter) {
        size = 0
        for (i=0; i<counter; i++) {
            size += carouselImages[i].clientWidth
        }
    }

    carouselNextButton.addEventListener('click', ()=>{
        if (counter >= carouselImages.length -1 )return;
        counter ++;
        changeSlide(counter);
    });

    carouselPreviousButton.addEventListener('click', ()=>{
        if (counter <= 0)return;
        counter --;
        changeSlide(counter);
    });

    carouselSlide.addEventListener('transitionend', ()=>{
        if (carouselImages[counter].id === 'lastClone'){
            carouselSlide.style.transition = "none";
            counter = carouselImages.length - 2;
            resize(counter)
            carouselSlide.style.transform = 'translateX(' + (-size) + 'px)';
        }
        else if(carouselImages[counter].id === 'firstClone'){
            carouselSlide.style.transition = "none";
            counter = 1;
            resize(counter)
            carouselSlide.style.transform = 'translateX(' + (-size) + 'px)';
        }
    });
}

for (i=0; i<updateCart.length; i++){
    updateCart[i].addEventListener('click', placeAction)
}

for (i=0; i<updateItem.length; i++){
    updateItem[i].addEventListener('input', placeAction)
}

function placeAction(){
    const productID = this.dataset.product
    const action = this.dataset.action

    if (user === 'AnonymousUser'){
        if (action === 'update-item'){
            addCookieItem(productID, action, this.value)
        }
        else{
            addCookieItem(productID, action)
        }
    }
    else {
        if (action === 'update-item'){
            updateUserOrder(productID, action, this.value)
        }
        else{
            updateUserOrder(productID, action)
        }
    }
}

function addCookieItem(productID, action, datavalue){
    if (action == 'add'){
        if (cart[productID] == undefined){
            cart[productID] = {'quantity': 1}
        }
        else {
            cart[productID]['quantity'] += 1
        }
    }
    else {
        if (action == 'remove'){
            cart[productID]['quantity'] -= 1
            if (cart[productID]['quantity'] <= 0){
                delete cart[productID]
            }
        }
        else if (action == 'update-item'){
            cart[productID]['quantity'] = parseInt(datavalue)
            if (cart[productID]['quantity'] <= 0){
                console.log('Remove Item')
                delete cart[productID]
            }
        }
    }

    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

    const url = '/item_updated/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        }
    })

    .then((response) => {
        return response.json()
    })

    .then((data) =>{
        console.log('data:', data)
        updateCartList(data)
    })
}


function updateUserOrder(productID, action, datavalue){
    console.log('User is logged in, sending data...')

    const url = '/item_updated/'

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
            'productID': productID,
            'action': action,
            'datavalue': datavalue
        })
    })

    .then((response) => {
        return response.json()
    })

    .then((data) =>{
        console.log('data:', data)
        updateCartList(data)
    })
}

function updateCartList(data){
    const items = JSON.parse(data.items)
    const cartItemsList = document.getElementById('cart-items-list')
    document.querySelector('.cart-number').innerHTML = data.cartItems
    if (cartItemsList){
        if (items.length > 0){
            cartItemsList.innerHTML = ''
            for (i=0; i<items.length; i++){
                itemCodeBlock = `<tr>
                                    <td><input type="checkbox"></td>
                                    <td>
                                        <a href="#">
                                            <div class="cart-product-img">
                                                <img src=${items[i].product.imageURL} alt="">
                                            </div>
                                                <span>${items[i].product.name}</span>
                                        </a>
                                    </td>
                                    <td>RM ${items[i].product.price}</td>
                                    <td><input data-product=${items[i].product.id} data-action="update-item" class="update-item" value=${items[i].quantity} type="number" min="0" wfd-id=${items[i].product.id}></td>
                                    <td>RM ${items[i].get_total}</td>
                                    <td>Delete</td>
                                </tr>`
                cartItemsList.innerHTML += itemCodeBlock
            }
        }
        else {
            cartItemsList.innerHTML = ''
        }
        document.getElementById('cart-total').innerHTML = data.order.get_cart_total
        const updateItem = document.querySelectorAll('.update-item');
        for (i=0; i<updateItem.length; i++){
            updateItem[i].addEventListener('input', placeAction)
        }
    }
}