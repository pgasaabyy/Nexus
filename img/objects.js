//médio
let aluno = {
    nome: "Luis",
    nota1: 7,
    nota2: 9,
    nota3: 8,
}
let média = (aluno.nota1 + aluno.nota2 + aluno.nota3) / 3;
console.log(média);


let produto ={
    preço: 800,
    quantidade: 400,
};
let Vt = produto.preço * produto.quantidade;
console.log(Vt);

let carro ={
   ano: 2008, 
};
console.log(carro.ano > 2015 ?"carro foi lançado depois de 2015":"carro foi lançado antes de 2015"); 


let pessoa ={
   idade: 17, 
};
console.log(pessoa.idade > 18 ?"maior de idade":"menor de idade"); 


let computador ={
    memoria: 10,
};
console.log(computador.memoria > 8 ? "Memória maior que 8" : "memória menor que 8");


let jogo={
    pontos: 10,
    bonus: 30,
};
console.log(jogo.pontos + jogo.bonus);


let produto1={
    preco: 100,
    desconto: 30,
};
console.log(produto1.desconto <= produto1.preco? "Sim o desconto é menor que o preço" : "Não o desconto é maior que o preço ");


let aluno1 ={
    nota4: 4,
    nota5: 9,
};
console.log(aluno1.nota4 + aluno1.nota5 == 10? "Sim a soma das notas é igual a 10" : "Não a soma das notas não equivalem a 10");


let livro ={
    paginas: 187,
};
console.log(livro.paginas % 2 == 0 ? "Sim o numero de pagina do livro é par" : "Não o numero de paginas não é par");


let cachorro ={
    idade5000: 19,
};
console.log(cachorro.idade5000 > 10 ? "A idade do cachorro é maior que 10" : "A idade do cachorro é menor que 10");

//facil

let pessoa1 ={
    nome: "Luiz",
    idade1: 17,
cidade: "São Paulo"
}
console.log(pessoa1.nome + pessoa1.idade1 + pessoa1.cidade)