FROM test-base

RUN dnf -y install dnf-plugins-core rpm-build createrepo_c

COPY test-build /var/tmp/test-build
RUN rm -rf /etc/yum.repos.d/*.repo

RUN cd /var/tmp
RUN rpmbuild -bb --define "_rpmdir $(pwd)" /var/tmp/test-build/kernel1/kernel.spec && dnf -y --disablerepo='*' install $(uname -p)/kernel*.rpm && mkdir -p /var/tmp/kernel1 && mv $(uname -p)/kernel*.rpm /var/tmp/kernel1
RUN rpmbuild -bb --define "_rpmdir $(pwd)" /var/tmp/test-build/kernel2/kernel.spec && mkdir -p /var/tmp/kernel2 && mv $(uname -p)/kernel*.rpm /var/tmp/kernel2
RUN rpmbuild -bb --define "_rpmdir $(pwd)" /var/tmp/test-build/kernel3/kernel.spec && mkdir -p /var/tmp/kernel3 && mv $(uname -p)/kernel*.rpm /var/tmp/kernel3
RUN rpmbuild -bb --define "_rpmdir $(pwd)" /var/tmp/test-build/kmod-test1/kmod-test.spec && mkdir -p /var/tmp/kmod-test1 && mv $(uname -p)/kmod-test*.rpm /var/tmp/kmod-test1
RUN rpmbuild -bb --define "_rpmdir $(pwd)" /var/tmp/test-build/kmod-test2/kmod-test.spec && mkdir -p /var/tmp/kmod-test2 && mv $(uname -p)/kmod-test*.rpm /var/tmp/kmod-test2

COPY tests /var/tmp/tests
RUN chmod 0755 /var/tmp/tests/run_test.sh

COPY src/protected_kmods.py /var/tmp/
RUN mv /var/tmp/protected_kmods.py /usr/lib/python3.*/site-packages/dnf-plugins/

CMD ["/var/tmp/tests/run_test.sh"]
