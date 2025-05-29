# code
1.Launch (step 1 - 2 - 3)
2.Update data (do step 1/2/3) just add new data (so check old data to compare)
3.Recover (step + token id)


## stat
rajouter au token bol no transaction / no data
been validated


correlation nombre de token creer par jour et le nombre de transaction et le volume en eth sur le launchpad et letat du btc/eth

faire la courbe de nb de token creer par j
// transaction
quelle portefeuille creer le plus de token / on le plus de gain via les transactions



## recherche :
timescale vs mongo pour du pytorch
workpool et atomicite (pour csv et db)


## data

When the curve hits 100%, the token will have reached a market cap of $69K and will be listed on Uniswap.

When the curve reaches 100%, the token will have reached a market cap of $34.5K and will replace the current "King of Apes" on the podium.

cas special quand le dev vend son supply

token valide = 69k market cap, ca fait combien en liquidity eth
courbe market cap / liquidity <- connaitre le nb de token en circulation (price x token)




La colonne tokenChange suffit :

Achat (Buy)
tokenChange > 0
nativeIn > 0 (l’utilisateur envoie de l’ETH)
nativeOut = 0
tokenIn = 0

Vente (Sell)
tokenChange < 0
nativeOut > 0 (l’utilisateur reçoit de l’ETH)
nativeIn = 0
tokenIn = tokenAddress

Mint (add liquidity)	tokenIn > 0 ET nativeIn > 0  ET tokenOut = nativeOut = 0
Burn (remove liquidity)	tokenOut > 0 ET nativeOut > 0 ET tokenIn = nativeIn = 0
Swap BUY (ETH → token)	tokenOut > 0 ET nativeIn > 0
Swap SELL (token → ETH)	tokenIn > 0 ET nativeOut > 0


## norma

mettre uniquement les donnees utile,
enelver les transaction post market cap de 70k si il y en a 

pour chaque transaction

donne vecteur y :
bool validated

donne fixe :
id token


donne variable :
marekt cap post transaction en dollar
liquidity post transaction en dollar
nb total tx buy
nb total tx sell
total volume of buy in eth
total volume of sell in eth
ssecond since deploy
bool creator of the token

eth in
token out
eth out
token in
price before
price after
price change
bool buy/sell transaction


donnee a derive en last 1s et last 10s:
volume achat
volume vente
tx sell
tx buy